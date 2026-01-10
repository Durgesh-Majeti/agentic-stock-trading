"""Unit tests for repositories."""
import pytest
from datetime import date
from database.repositories.market_data_repo import MarketDataRepository


def test_create_stock(temp_db):
    """Test stock creation."""
    repo = MarketDataRepository(temp_db)
    
    stock = repo.create_stock(
        symbol="TEST-EQ",
        name="Test Stock",
        exchange="NSE",
        sector="IT",
        market_cap=1000000000
    )
    
    assert stock.id is not None
    assert stock.symbol == "TEST-EQ"
    assert stock.name == "Test Stock"
    assert stock.sector == "IT"
    assert stock.market_cap == 1000000000


def test_get_stock_by_symbol(temp_db, sample_stock):
    """Test getting stock by symbol."""
    repo = MarketDataRepository(temp_db)
    
    found = repo.get_stock_by_symbol("TEST-EQ")
    assert found is not None
    assert found.symbol == "TEST-EQ"


def test_add_daily_data(temp_db, sample_stock):
    """Test adding daily market data."""
    repo = MarketDataRepository(temp_db)
    
    data = repo.add_daily_data(
        stock_id=sample_stock.id,
        date=date.today(),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000
    )
    
    assert data.id is not None
    assert data.close == 103.0


def test_get_latest_daily_data(temp_db, sample_stock):
    """Test getting latest daily data."""
    repo = MarketDataRepository(temp_db)
    
    # Add multiple days
    repo.add_daily_data(sample_stock.id, date(2024, 1, 1), 100, 105, 99, 103, 1000000)
    repo.add_daily_data(sample_stock.id, date(2024, 1, 2), 103, 108, 102, 106, 1100000)
    temp_db.commit()
    
    latest = repo.get_latest_daily_data(sample_stock.id)
    assert latest is not None
    assert latest.date == date(2024, 1, 2)


def test_update_stock_info(temp_db, sample_stock):
    """Test updating stock sector and market cap."""
    repo = MarketDataRepository(temp_db)
    
    # Update sector and market cap
    updated = repo.update_stock_info(
        stock_id=sample_stock.id,
        sector="Technology",
        market_cap=2000000000
    )
    
    assert updated is not None
    assert updated.sector == "Technology"
    assert updated.market_cap == 2000000000
    
    # Update only sector
    updated = repo.update_stock_info(
        stock_id=sample_stock.id,
        sector="IT Services"
    )
    assert updated.sector == "IT Services"
    assert updated.market_cap == 2000000000  # Should remain unchanged
