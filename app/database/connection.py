import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator
import logging

from app.database.models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            print("❌ DATABASE_URL environment variable is not set!")
            print("Current environment variables:")
            for key in os.environ:
                if 'DATABASE' in key.upper():
                    print(f"  {key}: {os.environ[key]}")
            raise ValueError("DATABASE_URL environment variable is required. Make sure load_dotenv() is called before importing this module.")
        
        print(f"✅ Database URL loaded: {self.database_url[:30]}...")  # Only show first 30 chars for security
        
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global instance
db_manager = DatabaseManager()