from app.database.connection import db_manager
from app.database.repositories import UserRepository, QueryHistoryRepository
from app.database.models import User, QueryHistory
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class QueryPersistenceService:
    def __init__(self):
        self.db_manager = db_manager
    
    def save_query_and_results(
        self,
        user_id: int,
        user_query: str,
        pandas_query: str,
        execution_time_ms: int,
        result_count: int,
        status: str,
        error_message: str = None
    ) -> Optional[int]:
        """Save query to database and return query ID"""
        try:
            with self.db_manager.get_session() as session:
                query_repo = QueryHistoryRepository(session)
                query = query_repo.save_query(
                    user_id=user_id,
                    user_query=user_query,
                    pandas_query=pandas_query,
                    execution_time_ms=execution_time_ms,
                    result_count=result_count,
                    status=status,
                    error_message=error_message
                )
                return query.id
        except Exception as e:
            logger.error(f"Error saving query: {e}")
            return None
    
    def get_or_create_anonymous_user(self) -> Optional[int]:
        """Get or create anonymous user and return user ID"""
        try:
            with self.db_manager.get_session() as session:
                user_repo = UserRepository(session)
                user = user_repo.create_anonymous_user()
                return user.id
        except Exception as e:
            logger.error(f"Error creating anonymous user: {e}")
            return None
    
    def get_user_query_history(self, user_id: int, limit: int = 50) -> List[QueryHistory]:
        """Get user's query history"""
        try:
            with self.db_manager.get_session() as session:
                query_repo = QueryHistoryRepository(session)
                return query_repo.get_user_queries(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting user queries: {e}")
            return []

# Global instance
query_service = QueryPersistenceService()