from app.database.models import QueryHistory
from typing import Optional, List

class QueryPersistenceService:
    def __init__(self):
        self.db_enabled = False
    
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
        """Database disabled: keep method signature but do not persist."""
        _ = (user_id, user_query, pandas_query, execution_time_ms, result_count, status, error_message)
        return None
    
    def get_or_create_anonymous_user(self) -> Optional[int]:
        """Database disabled: no user record is created."""
        return None
    
    def get_user_query_history(self, user_id: int, limit: int = 50) -> List[QueryHistory]:
        """Database disabled: return an empty history."""
        _ = (user_id, limit)
        return []

# Global instance
query_service = QueryPersistenceService()