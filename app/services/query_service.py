import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.database.models import FoodSearchHistory

logger = logging.getLogger(__name__)


class QueryPersistenceService:
    def save_search(
        self, user_query: str, username: Optional[str], email: Optional[str], is_anonymous: bool
    ) -> None:
        logger.info("Saving food search")
        try:
            from app.database.connection import db_manager

            with db_manager.get_session() as session:
                session.add(FoodSearchHistory(
                    user_query=user_query,
                    username=username,
                    email=email,
                    is_anonymous=is_anonymous,
                ))
        except (SQLAlchemyError, ValueError) as exc:
            logger.error("Could not save food search (%s)", type(exc).__name__)


query_service = QueryPersistenceService()