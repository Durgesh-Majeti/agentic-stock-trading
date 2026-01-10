"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
import sys
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import Base
from database.session import SessionLocal


@pytest.fixture(scope="function")
def temp_db():
    """Create temporary database for testing."""
    import os
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Create engine and tables
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def sample_stock(temp_db):
    """Create sample stock for testing."""
    from database.models import Stock
    from config.constants import Exchange
    
    stock = Stock(
        symbol="TEST-EQ",
        name="Test Stock",
        exchange=Exchange.NSE,
        sector="IT",
        market_cap=1000000000
    )
    temp_db.add(stock)
    temp_db.commit()
    temp_db.refresh(stock)
    return stock


@pytest.fixture(scope="function")
def sample_market_data(temp_db, sample_stock):
    """Create sample market data for testing."""
    from database.models import MarketDataDaily
    from datetime import date
    
    data = MarketDataDaily(
        stock_id=sample_stock.id,
        date=date.today(),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000,
        rsi=28.5
    )
    temp_db.add(data)
    temp_db.commit()
    temp_db.refresh(data)
    return data
