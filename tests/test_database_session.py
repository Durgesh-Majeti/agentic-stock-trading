"""Unit tests for database session."""
import pytest
from database.models import Stock
from sqlalchemy import text, inspect


def test_get_db_context_manager(temp_db):
    """Test database context manager."""
    # Test query
    result = temp_db.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_database_initialization(temp_db):
    """Test database initialization."""
    # Check tables exist
    inspector = inspect(temp_db.bind)
    tables = inspector.get_table_names()
    
    assert "stocks" in tables
    assert "market_data_daily" in tables


def test_database_transaction_rollback(temp_db):
    """Test transaction rollback."""
    stock = Stock(symbol="TEST", name="Test", exchange="NSE")
    temp_db.add(stock)
    
    # Rollback
    temp_db.rollback()
    
    # Should not exist
    from sqlalchemy.orm import Query
    result = temp_db.query(Stock).filter_by(symbol="TEST").first()
    assert result is None
