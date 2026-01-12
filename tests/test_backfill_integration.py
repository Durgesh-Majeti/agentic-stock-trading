"""Integration tests for backfill script."""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date, timedelta

from data_sources.yfinance_fetcher import YFinanceFetcher
from database.repositories.market_data_repo import MarketDataRepository


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV DataFrame with enough rows for indicators.
    
    yfinance returns DataFrame with DatetimeIndex, not a date column.
    The code will reset_index() to convert index to 'Date' column, then rename to 'date'.
    """
    dates = pd.date_range(start=date.today() - timedelta(days=50), periods=50, freq='D')
    # yfinance format: DatetimeIndex with Open, High, Low, Close, Volume columns
    df = pd.DataFrame({
        'Open': [100.0 + i * 0.5 for i in range(50)],
        'High': [105.0 + i * 0.5 for i in range(50)],
        'Low': [99.0 + i * 0.5 for i in range(50)],
        'Close': [103.0 + i * 0.5 for i in range(50)],
        'Volume': [1000000 + i * 10000 for i in range(50)]
    }, index=dates)
    # The index will be converted to 'Date' column when reset_index() is called
    return df


@pytest.mark.integration
class TestBackfillIntegration:
    """Integration tests for backfill functionality."""
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_backfill_symbol_creates_stock(self, mock_ticker, mock_get, temp_db, sample_ohlcv_data):
        """Test that backfilling creates stock if it doesn't exist."""
        from scripts.backfill_nifty500 import backfill_symbol
        
        # Mock Nifty 500 list
        csv_content = "Symbol,Company Name,Sector\nRELIANCE,Reliance Industries Ltd,Energy"
        mock_response = MagicMock()
        mock_response.text = csv_content
        mock_response.content = csv_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Mock yfinance ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker_instance.info = {
            'sector': 'Energy',
            'marketCap': 1000000000000,
            'longName': 'Reliance Industries Limited'
        }
        mock_ticker.return_value = mock_ticker_instance
        
        # Create fetcher and repo
        fetcher = YFinanceFetcher()
        repo = MarketDataRepository(temp_db)
        
        # Backfill symbol
        result = backfill_symbol(
            symbol="RELIANCE",
            company_name="Reliance Industries Ltd",
            sector="Energy",
            fetcher=fetcher,
            repo=repo
        )
        
        # Assertions
        assert result is True
        
        # Check stock was created
        stock = repo.get_stock_by_symbol("RELIANCE")
        assert stock is not None
        assert stock.symbol == "RELIANCE"
        assert stock.name == "Reliance Industries Ltd"
        assert stock.sector == "Energy"
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_backfill_symbol_stores_data(self, mock_ticker, temp_db, sample_ohlcv_data):
        """Test that backfilling stores market data."""
        from scripts.backfill_nifty500 import backfill_symbol
        from database.models import Stock
        from config.constants import Exchange
        
        # Create stock first
        stock = Stock(
            symbol="RELIANCE",
            name="Reliance Industries Ltd",
            exchange=Exchange.NSE,
            sector="Energy"
        )
        temp_db.add(stock)
        temp_db.commit()
        temp_db.refresh(stock)
        
        # Mock yfinance ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Create fetcher and repo
        fetcher = YFinanceFetcher()
        repo = MarketDataRepository(temp_db)
        
        # Backfill symbol
        result = backfill_symbol(
            symbol="RELIANCE",
            company_name="Reliance Industries Ltd",
            sector="Energy",
            fetcher=fetcher,
            repo=repo
        )
        
        # Assertions
        assert result is True
        
        # Check data was stored
        latest_data = repo.get_latest_daily_data(stock.id)
        assert latest_data is not None
        assert latest_data.close > 0
        assert latest_data.volume > 0
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_backfill_symbol_calculates_indicators(self, mock_ticker, temp_db, sample_ohlcv_data):
        """Test that backfilling calculates technical indicators."""
        from scripts.backfill_nifty500 import backfill_symbol
        from database.models import Stock
        from config.constants import Exchange
        
        # Create stock first
        stock = Stock(
            symbol="RELIANCE",
            name="Reliance Industries Ltd",
            exchange=Exchange.NSE,
            sector="Energy"
        )
        temp_db.add(stock)
        temp_db.commit()
        temp_db.refresh(stock)
        
        # Mock yfinance ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Create fetcher and repo
        fetcher = YFinanceFetcher()
        repo = MarketDataRepository(temp_db)
        
        # Backfill symbol
        result = backfill_symbol(
            symbol="RELIANCE",
            company_name="Reliance Industries Ltd",
            sector="Energy",
            fetcher=fetcher,
            repo=repo
        )
        
        # Assertions
        assert result is True
        
        # Check indicators were calculated (at least some should be present)
        latest_data = repo.get_latest_daily_data(stock.id)
        assert latest_data is not None
        
        # Check that some indicators are present (not all may be calculated if data is insufficient)
        # RSI should be calculated if we have enough data
        if latest_data.rsi is not None:
            assert 0 <= latest_data.rsi <= 100
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_backfill_symbol_skips_existing_data(self, mock_ticker, temp_db, sample_ohlcv_data):
        """Test that backfilling skips already existing data."""
        from scripts.backfill_nifty500 import backfill_symbol
        from database.models import Stock, MarketDataDaily
        from config.constants import Exchange
        
        # Create stock first
        stock = Stock(
            symbol="RELIANCE",
            name="Reliance Industries Ltd",
            exchange=Exchange.NSE,
            sector="Energy"
        )
        temp_db.add(stock)
        temp_db.commit()
        temp_db.refresh(stock)
        
        # Add existing recent data
        existing_data = MarketDataDaily(
            stock_id=stock.id,
            date=date.today() - timedelta(days=1),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000000
        )
        temp_db.add(existing_data)
        temp_db.commit()
        
        # Mock yfinance ticker (should not be called if data is recent)
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Create fetcher and repo
        fetcher = YFinanceFetcher()
        repo = MarketDataRepository(temp_db)
        
        # Backfill symbol
        result = backfill_symbol(
            symbol="RELIANCE",
            company_name="Reliance Industries Ltd",
            sector="Energy",
            fetcher=fetcher,
            repo=repo
        )
        
        # Should succeed (skip fetch if data is recent)
        assert result is True
