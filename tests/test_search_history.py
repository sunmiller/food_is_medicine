import os
import sys
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.sessions import SessionMiddleware

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from app.routers import food


class SearchHistoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        with self.engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE food_search_history (
                    id INTEGER PRIMARY KEY,
                    user_query TEXT NOT NULL,
                    username TEXT,
                    email TEXT,
                    is_anonymous BOOLEAN NOT NULL,
                    searched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))

        session_factory = sessionmaker(bind=self.engine)

        @contextmanager
        def get_session():
            with session_factory.begin() as session:
                yield session

        self.manager = SimpleNamespace(get_session=get_session)
        self.connection_patch = patch.dict(
            sys.modules,
            {"app.database.connection": SimpleNamespace(db_manager=self.manager)},
        )
        self.connection_patch.start()
        self.addCleanup(self.connection_patch.stop)
        self.addCleanup(self.engine.dispose)

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-key")
        app.include_router(food.router)

        @app.post("/test-sign-in")
        def sign_in(request: Request):
            name = None if request.query_params.get("without_name") else "Example User"
            email = None if request.query_params.get("without_email") else "user@example.com"
            request.session["user"] = {"name": name, "email": email, "sub": "123"}

        self.client = TestClient(app)
        self.query_patch = patch.object(food, "run_food_query", return_value={"results": []})
        self.query_patch.start()
        self.addCleanup(self.query_patch.stop)

    def test_saves_each_search_with_session_identity(self):
        self.assertEqual(self.client.post("/search", data={"query": "apple"}).status_code, 200)
        self.assertEqual(self.client.post("/test-sign-in").status_code, 200)
        self.assertEqual(self.client.post("/search", data={"query": "banana"}).status_code, 200)
        self.assertEqual(self.client.post("/search", data={"query": "banana"}).status_code, 200)
        self.assertEqual(self.client.post("/test-sign-in?without_name=1&without_email=1").status_code, 200)
        self.assertEqual(self.client.post("/search", data={"query": "pear"}).status_code, 200)
        self.assertEqual(self.client.post("/search", data={"query": "   "}).status_code, 200)

        with self.engine.connect() as connection:
            rows = connection.execute(text(
                "SELECT user_query, username, email, is_anonymous, searched_at "
                "FROM food_search_history ORDER BY id"
            )).all()

        self.assertEqual([tuple(row[:4]) for row in rows], [
            ("apple", None, None, 1),
            ("banana", "Example User", "user@example.com", 0),
            ("banana", "Example User", "user@example.com", 0),
            ("pear", None, None, 0),
        ])
        self.assertTrue(all(row.searched_at is not None for row in rows))

    def test_database_failure_does_not_break_search_or_log_query(self):
        @contextmanager
        def failing_session():
            raise OperationalError("private query", {}, Exception("database unavailable"))
            yield

        self.manager.get_session = failing_session
        with self.assertLogs("app.services.query_service", level="ERROR") as logs:
            response = self.client.post("/search", data={"query": "private query"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("No results found", response.text)
        self.assertNotIn("private query", "\n".join(logs.output))

    def test_saves_before_search_processing_failure(self):
        with patch.object(food, "run_food_query", side_effect=RuntimeError("search failed")):
            with self.assertRaisesRegex(RuntimeError, "search failed"):
                self.client.post("/search", data={"query": "apple"})

        with self.engine.connect() as connection:
            count = connection.execute(text(
                "SELECT COUNT(*) FROM food_search_history WHERE user_query = 'apple'"
            )).scalar_one()
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
