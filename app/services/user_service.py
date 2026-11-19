import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.database.repositories import UserRepository

logger = logging.getLogger(__name__)


def save_google_user(
    google_sub: Optional[str], email: Optional[str], name: Optional[str], picture: Optional[str]
) -> None:
    if not google_sub:
        logger.error("Could not save Google user: missing account ID")
        return

    try:
        from app.database.connection import db_manager

        with db_manager.get_session() as session:
            UserRepository(session).save_google_user(google_sub, email, name, picture)
    except (SQLAlchemyError, ValueError) as exc:
        logger.error("Could not save Google user (%s)", type(exc).__name__)
