"""Unit tests for data_source_manager."""
import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
from datetime import date, timedelta, datetime

from data_sources.data_source_manager import DataSourceManager


@pytest.fixture
def data_source_manager():
    """Create DataSourceManager instance."""
    return DataSourceManager()


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV DataFrame."""
    dates = pd.date_range(start=date.today() - timedelta(days=5), periods=5, freq='D')
    return pd.DataFrame({
        'date': dates.date,
        'open': [100.0 + i * 0.5 for i in range(5)],
        'high': [105.0 + i * 0.5 for i in range(5)],
        'low': [99.0 + i * 0.5 for i in range(5)],
        'close': [103.0 + i * 0.5 for i in range(5)],
        'volume': [1000000 + i * 10000 for i in range(5)]
    })


class TestDataSourceManager:
    """Test cases for DataSourceManager."""
    
    def test_init(self, data_source_manager):
        """Test DataSourceManager initialization."""
        assert data_source_manager.primary_source == "yfinance"
        assert data_source_manager.backup_source == "yfinance"
        assert data_source_manager.yfinance_fetcher is not None
        assert data_source_manager.data_freshness_threshold == timedelta(minutes=2)
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.get_historical_data')
    def test_get_historical_data_success(self, mock_get_data, data_source_manager, sample_ohlcv_data):
        """Test successful getting of historical data."""
        mock_get_data.return_value = sample_ohlcv_data
        
        result = data_source_manager.get_historical_data("RELIANCE", period="5d")
        
        assert result is not None
        assert len(result) == 5
        mock_get_data.assert_called_once_with(
            symbol="RELIANCE",
            start_date=None,
            end_date=None,
            period="5d"
        )
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.get_historical_data')
    def test_get_historical_data_with_date_range(self, mock_get_data, data_source_manager, sample_ohlcv_data):
        """Test getting historical data with date range."""
        mock_get_data.return_value = sample_ohlcv_data
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        result = data_source_manager.get_historical_data(
            "RELIANCE",
            start_date=start_date,
            end_date=end_date
        )
        
        assert result is not None
        mock_get_data.assert_called_once_with(
            symbol="RELIANCE",
            start_date=start_date,
            end_date=end_date,
            period="2y"
        )
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.get_historical_data')
    def test_get_historical_data_handles_failure(self, mock_get_data, data_source_manager):
        """Test handling of data fetch failure."""
        mock_get_data.return_value = None
        
        result = data_source_manager.get_historical_data("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.get_historical_data')
    def test_get_historical_data_handles_exception(self, mock_get_data, data_source_manager):
        """Test handling of exceptions during data fetch."""
        mock_get_data.side_effect = Exception("Network error")
        
        result = data_source_manager.get_historical_data("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.data_source_manager.DataSourceManager.get_historical_data')
    def test_get_latest_price_success(self, mock_get_data, data_source_manager, sample_ohlcv_data):
        """Test successful getting of latest price."""
        mock_get_data.return_value = sample_ohlcv_data
        
        result = data_source_manager.get_latest_price("RELIANCE")
        
        assert result is not None
        assert result['symbol'] == "RELIANCE"
        assert result['open'] == 102.0  # Last row in sample data
        assert result['high'] == 107.0
        assert result['low'] == 101.0
        assert result['close'] == 105.0
        assert result['volume'] == 1040000  # Last row: 1000000 + 4*10000
        assert 'timestamp' in result
        mock_get_data.assert_called_once_with("RELIANCE", period="5d")
    
    @patch('data_sources.data_source_manager.DataSourceManager.get_historical_data')
    def test_get_latest_price_handles_no_data(self, mock_get_data, data_source_manager):
        """Test handling of no data available."""
        mock_get_data.return_value = None
        
        result = data_source_manager.get_latest_price("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.data_source_manager.DataSourceManager.get_historical_data')
    def test_get_latest_price_handles_empty_dataframe(self, mock_get_data, data_source_manager):
        """Test handling of empty DataFrame."""
        mock_get_data.return_value = pd.DataFrame()
        
        result = data_source_manager.get_latest_price("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.data_source_manager.DataSourceManager.get_historical_data')
    def test_get_latest_price_warns_old_data(self, data_source_manager):
        """Test warning for old data."""
        old_date = date.today() - timedelta(days=5)
        old_data = pd.DataFrame({
            'date': [old_date],
            'open': [100.0],
            'high': [105.0],
            'low': [99.0],
            'close': [103.0],
            'volume': [1000000]
        })
        
        with patch.object(data_source_manager, 'get_historical_data', return_value=old_data):
            result = data_source_manager.get_latest_price("RELIANCE")
            
            # Should still return data but it's old
            assert result is not None
    
    def test_validate_data_freshness_fresh(self, data_source_manager):
        """Test validation of fresh data."""
        timestamp = datetime.now() - timedelta(minutes=1)
        
        assert data_source_manager.validate_data_freshness(timestamp) is True
    
    def test_validate_data_freshness_stale(self, data_source_manager):
        """Test validation of stale data."""
        timestamp = datetime.now() - timedelta(minutes=5)
        
        assert data_source_manager.validate_data_freshness(timestamp) is False
    
    def test_validate_data_freshness_custom_threshold(self, data_source_manager):
        """Test validation with custom threshold."""
        timestamp = datetime.now() - timedelta(minutes=10)
        custom_threshold = timedelta(minutes=15)
        
        assert data_source_manager.validate_data_freshness(timestamp, max_age=custom_threshold) is True
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.batch_fetch_historical_data')
    def test_batch_get_historical_data(self, mock_batch_fetch, data_source_manager, sample_ohlcv_data):
        """Test batch getting of historical data."""
        mock_batch_fetch.return_value = {
            "RELIANCE": sample_ohlcv_data,
            "TCS": sample_ohlcv_data,
            "HDFCBANK": sample_ohlcv_data
        }
        
        symbols = ["RELIANCE", "TCS", "HDFCBANK"]
        results = data_source_manager.batch_get_historical_data(
            symbols=symbols,
            period="5d",
            batch_size=2
        )
        
        assert len(results) == 3
        assert all(symbol in results for symbol in symbols)
        mock_batch_fetch.assert_called_once_with(
            symbols=symbols,
            period="5d",
            batch_size=2,
            delay_between_batches=1.0
        )
    
    @patch('data_sources.data_source_manager.YFinanceFetcher.get_nifty_500_symbols')
    def test_get_nifty_500_symbols(self, mock_get_symbols, data_source_manager):
        """Test getting Nifty 500 symbols."""
        mock_get_symbols.return_value = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'sector': 'Energy'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy', 'sector': 'IT'}
        ]
        
        result = data_source_manager.get_nifty_500_symbols()
        
        assert len(result) == 2
        assert result[0]['symbol'] == 'RELIANCE'
        mock_get_symbols.assert_called_once()
