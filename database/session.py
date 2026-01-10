"""Database session management."""
from sqlalchemy import create_engine, event
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
        "timeout": 30,  # Increase timeout for bulk operations
    },
    poolclass=StaticPool,  # SQLite doesn't support connection pooling
    echo=False,  # Set to True for SQL query logging
)

# Enable WAL mode and optimize SQLite settings for better performance
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better performance."""
    cursor = dbapi_conn.cursor()
    # Enable WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    # Normal synchronous mode (faster than FULL, still safe)
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Increase cache size (default is 2000 pages, ~2MB)
    cursor.execute("PRAGMA cache_size=10000")  # ~10MB cache
    # Store temporary tables in memory
    cursor.execute("PRAGMA temp_store=MEMORY")
    # Increase page size for better performance (if not already set)
    cursor.execute("PRAGMA page_size=4096")
    cursor.close()

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
        # Only commit if there are pending changes and no errors
        if session.is_active:
            try:
                session.commit()
            except Exception as commit_error:
                logger.error(f"Commit error: {commit_error}")
                session.rollback()
                raise
    except Exception as e:
        logger.error(f"Database error: {e}")
        # Rollback only if session is active
        try:
            if session.is_active:
                session.rollback()
        except Exception as rollback_error:
            # If rollback fails, log but don't raise (session might already be closed)
            logger.warning(f"Rollback error (session may be closed): {rollback_error}")
        raise
    finally:
        try:
            session.close()
        except Exception as close_error:
            # Log but don't raise - session might already be closed
            logger.warning(f"Error closing session: {close_error}")


def init_db() -> None:
    """Initialize database - create all tables."""
    from database.models import Base
    
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
