"""
Database configuration and session management for Contact Reconciliation Service.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database URL - uses environment variable or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contacts.db")

# Create SQLAlchemy engine
# check_same_thread=False is needed for SQLite to work with multiple threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True for debugging
)

# Create sessionmaker for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    This function will be used with FastAPI's dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    This function should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)
