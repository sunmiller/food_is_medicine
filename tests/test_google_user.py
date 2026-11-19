import os
import sys
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.sessions import SessionMiddleware

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from app.routers import food


class GoogleUserTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        with self.engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE,
                    google_sub TEXT UNIQUE,
                    name TEXT,
                    picture TEXT,
                    is_anonymous BOOLEAN NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """))

        session_factory = sessionmaker(bind=self.engine)

        @contextmanager
        def get_session():
            with session_factory.begin() as session:
                yield session

        self.manager = SimpleNamespace(get_session=get_session)
        connection_patch = patch.dict(
            sys.modules,
            {"app.database.connection": SimpleNamespace(db_manager=self.manager)},
        )
        connection_patch.start()
        self.addCleanup(connection_patch.stop)
        self.addCleanup(self.engine.dispose)

        self.google = SimpleNamespace(authorize_access_token=AsyncMock())
        patches = (
            patch.object(food, "google_client_id", "client-id"),
            patch.object(food, "google_client_secret", "client-secret"),
            patch.object(food, "oauth", SimpleNamespace(google=self.google)),
        )
        for item in patches:
            item.start()
            self.addCleanup(item.stop)

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-key")
        app.include_router(food.router)
        self.client = TestClient(app)

    def login(self, user_info):
        self.google.authorize_access_token.return_value = {"userinfo": user_info}
        return self.client.get("/auth/google/callback", follow_redirects=False)

    def test_login_creates_and_updates_one_user_per_google_account(self):
        user = {
            "sub": "google-1",
            "email": "first@example.com",
            "name": "First Name",
            "picture": "https://example.com/first.png",
        }
        self.assertEqual(self.login(user).status_code, 302)
        user.update(email="updated@example.com", name="Updated Name", picture="https://example.com/new.png")
        self.assertEqual(self.login(user).status_code, 302)
        self.assertEqual(self.login({"sub": "google-2"}).status_code, 302)

        with self.engine.connect() as connection:
            rows = connection.execute(text(
                "SELECT google_sub, email, name, picture, is_anonymous, created_at "
                "FROM users ORDER BY id"
            )).all()

        self.assertEqual([tuple(row[:5]) for row in rows], [
            ("google-1", "updated@example.com", "Updated Name", "https://example.com/new.png", 0),
            ("google-2", None, None, None, 0),
        ])
        self.assertTrue(all(row.created_at is not None for row in rows))

    def test_database_failure_does_not_block_login_or_log_personal_data(self):
        @contextmanager
        def failing_session():
            raise OperationalError("private email", {}, Exception("database unavailable"))
            yield

        self.manager.get_session = failing_session
        user = {"sub": "google-1", "email": "private email", "name": "Example User"}
        with self.assertLogs("app.services.user_service", level="ERROR") as logs:
            response = self.login(user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "/")
        self.assertIn("Example User", self.client.get("/").text)
        self.assertNotIn("private email", "\n".join(logs.output))

    def test_missing_google_id_is_logged_without_blocking_login(self):
        with self.assertLogs("app.services.user_service", level="ERROR") as logs:
            response = self.login({"name": "Example User"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("missing account ID", "\n".join(logs.output))
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT COUNT(*) FROM users")).scalar_one(), 0)

    def test_existing_email_is_not_linked_to_another_google_account(self):
        self.login({"sub": "google-1", "email": "user@example.com"})
        with self.assertLogs("app.services.user_service", level="ERROR"):
            response = self.login({"sub": "google-2", "email": "user@example.com"})

        self.assertEqual(response.status_code, 302)
        with self.engine.connect() as connection:
            subjects = connection.execute(text("SELECT google_sub FROM users")).scalars().all()
        self.assertEqual(subjects, ["google-1"])


if __name__ == "__main__":
    unittest.main()
