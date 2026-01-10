"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
from config.settings import settings
from loguru import logger


# Create engine with SQLite-specific configuration
engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,  # Needed for SQLite
    },
    poolclass=StaticPool,  # SQLite doesn't support connection pooling
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session (context manager).
    
    Yields:
        Database session
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager for database session.
    
    Yields:
        Database session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database - create all tables."""
    from database.models import Base
    
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
