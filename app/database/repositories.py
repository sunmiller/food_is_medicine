from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.models import User, QueryHistory
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create_anonymous_user(self) -> User:
        """Create a new anonymous user"""
        user = User(is_anonymous=True)
        self.session.add(user)
        self.session.flush()  # Get the ID without committing
        return user
    
    def create_user(self, email: str) -> User:
        """Create a new user with email"""
        user = User(email=email, is_anonymous=False)
        self.session.add(user)
        self.session.flush()
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()

class QueryHistoryRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def save_query(
        self,
        user_id: int,
        user_query: str,
        pandas_query: str,
        execution_time_ms: int,
        result_count: int,
        status: str,
        error_message: str = None
    ) -> QueryHistory:
        """Save a query to the database"""
        query = QueryHistory(
            user_id=user_id,
            user_query=user_query,
            pandas_query=pandas_query,
            execution_time_ms=execution_time_ms,
            result_count=result_count,
            status=status,
            error_message=error_message
        )
        self.session.add(query)
        self.session.flush()
        return query
    
    def get_user_queries(self, user_id: int, limit: int = 50) -> List[QueryHistory]:
        """Get recent queries for a user"""
        return (
            self.session.query(QueryHistory)
            .filter(QueryHistory.user_id == user_id)
            .order_by(desc(QueryHistory.query_timestamp))
            .limit(limit)
            .all()
        )
    
    def get_popular_queries(self, limit: int = 20) -> List[tuple]:
        """Get most popular queries"""
        return (
            self.session.query(
                QueryHistory.user_query,
                func.count(QueryHistory.id).label('frequency')
            )
            .filter(QueryHistory.status == 'success')
            .group_by(QueryHistory.user_query)
            .order_by(desc('frequency'))
            .limit(limit)
            .all()
        )