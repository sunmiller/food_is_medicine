from sqlalchemy import BigInteger, Boolean, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(Text, unique=True, nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    queries: Mapped[list["QueryHistory"]] = relationship("QueryHistory", back_populates="user")

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    pandas_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="queries")