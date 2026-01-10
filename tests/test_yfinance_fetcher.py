"""Unit tests for yfinance_fetcher."""
import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
from datetime import date, timedelta
import io

from data_sources.yfinance_fetcher import YFinanceFetcher


@pytest.fixture
def yfinance_fetcher():
    """Create YFinanceFetcher instance."""
    return YFinanceFetcher()


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for Nifty 500 list."""
    return """Symbol,Company Name,Sector
RELIANCE,Reliance Industries Ltd,Energy
TCS,Tata Consultancy Services Ltd,Information Technology
HDFCBANK,HDFC Bank Ltd,Financial Services"""


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV DataFrame."""
    dates = pd.date_range(start=date.today() - timedelta(days=30), periods=30, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Open': [100.0 + i * 0.5 for i in range(30)],
        'High': [105.0 + i * 0.5 for i in range(30)],
        'Low': [99.0 + i * 0.5 for i in range(30)],
        'Close': [103.0 + i * 0.5 for i in range(30)],
        'Volume': [1000000 + i * 10000 for i in range(30)]
    })


class TestYFinanceFetcher:
    """Test cases for YFinanceFetcher."""
    
    def test_init(self, yfinance_fetcher):
        """Test YFinanceFetcher initialization."""
        assert yfinance_fetcher.base_url == "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    def test_get_nifty_500_symbols_success(self, mock_get, yfinance_fetcher, sample_csv_content):
        """Test successful fetching of Nifty 500 symbols."""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = sample_csv_content
        mock_response.content = sample_csv_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call method
        symbols = yfinance_fetcher.get_nifty_500_symbols()
        
        # Assertions
        assert len(symbols) == 3
        assert symbols[0]['symbol'] == 'RELIANCE'
        assert symbols[0]['name'] == 'Reliance Industries Ltd'
        assert symbols[0]['sector'] == 'Energy'
        assert symbols[1]['symbol'] == 'TCS'
        assert symbols[2]['symbol'] == 'HDFCBANK'
        mock_get.assert_called_once()
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    def test_get_nifty_500_symbols_removes_ns_suffix(self, mock_get, yfinance_fetcher):
        """Test that .NS suffix is removed from symbols."""
        csv_content = "Symbol,Company Name\nRELIANCE.NS,Reliance Industries Ltd"
        mock_response = MagicMock()
        mock_response.text = csv_content
        mock_response.content = csv_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        symbols = yfinance_fetcher.get_nifty_500_symbols()
        
        assert symbols[0]['symbol'] == 'RELIANCE'
        assert symbols[0]['symbol'].endswith('.NS') is False
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    def test_get_nifty_500_symbols_removes_dash_suffix(self, mock_get, yfinance_fetcher):
        """Test that -EQ suffix is removed from symbols."""
        csv_content = "Symbol,Company Name\nRELIANCE-EQ,Reliance Industries Ltd"
        mock_response = MagicMock()
        mock_response.text = csv_content
        mock_response.content = csv_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        symbols = yfinance_fetcher.get_nifty_500_symbols()
        
        assert symbols[0]['symbol'] == 'RELIANCE'
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    def test_get_nifty_500_symbols_handles_missing_sector(self, mock_get, yfinance_fetcher):
        """Test handling of missing sector information."""
        # NSE format but with empty Industry column
        csv_content = "Company Name,Industry,Symbol,Series,ISIN Code\nReliance Industries Ltd,,RELIANCE,EQ,INE002A01018"
        mock_response = MagicMock()
        mock_response.text = csv_content
        mock_response.content = csv_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        symbols = yfinance_fetcher.get_nifty_500_symbols()
        
        assert len(symbols) == 1
        assert symbols[0]['symbol'] == 'RELIANCE'
        assert symbols[0]['sector'] is None or symbols[0]['sector'] == ''  # Empty string or None
    
    @patch('data_sources.yfinance_fetcher.requests.get')
    def test_get_nifty_500_symbols_handles_network_error(self, mock_get, yfinance_fetcher):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            yfinance_fetcher.get_nifty_500_symbols()
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_success(self, mock_ticker, yfinance_fetcher, sample_ohlcv_data):
        """Test successful fetching of historical data."""
        # Mock ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Call method
        result = yfinance_fetcher.get_historical_data("RELIANCE", period="1mo")
        
        # Assertions
        assert result is not None
        assert len(result) == 30
        assert 'date' in result.columns
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        mock_ticker.assert_called_once_with("RELIANCE.NS")
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_adds_ns_suffix(self, mock_ticker, yfinance_fetcher, sample_ohlcv_data):
        """Test that .NS suffix is added for NSE stocks."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        yfinance_fetcher.get_historical_data("RELIANCE")
        
        mock_ticker.assert_called_once_with("RELIANCE.NS")
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_with_date_range(self, mock_ticker, yfinance_fetcher, sample_ohlcv_data):
        """Test fetching historical data with date range."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        yfinance_fetcher.get_historical_data(
            "RELIANCE",
            start_date=start_date,
            end_date=end_date
        )
        
        mock_ticker_instance.history.assert_called_once_with(
            start=start_date,
            end=end_date,
            interval="1d",
            auto_adjust=True,
            prepost=False
        )
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_handles_empty_data(self, mock_ticker, yfinance_fetcher):
        """Test handling of empty data response."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        result = yfinance_fetcher.get_historical_data("INVALID")
        
        assert result is None
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_handles_missing_columns(self, mock_ticker, yfinance_fetcher):
        """Test handling of missing required columns."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame({'Date': [date.today()]})
        mock_ticker.return_value = mock_ticker_instance
        
        result = yfinance_fetcher.get_historical_data("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_historical_data_handles_errors(self, mock_ticker, yfinance_fetcher):
        """Test handling of yfinance errors."""
        mock_ticker.side_effect = Exception("yfinance error")
        
        result = yfinance_fetcher.get_historical_data("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_company_info_success(self, mock_ticker, yfinance_fetcher):
        """Test successful fetching of company info."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'sector': 'Energy',
            'industry': 'Oil & Gas',
            'marketCap': 1000000000000,
            'longName': 'Reliance Industries Limited'
        }
        mock_ticker.return_value = mock_ticker_instance
        
        result = yfinance_fetcher.get_company_info("RELIANCE")
        
        assert result is not None
        assert result['sector'] == 'Energy'
        assert result['industry'] == 'Oil & Gas'
        assert result['market_cap'] == 1000000000000
        assert result['long_name'] == 'Reliance Industries Limited'
    
    @patch('data_sources.yfinance_fetcher.yf.Ticker')
    def test_get_company_info_handles_errors(self, mock_ticker, yfinance_fetcher):
        """Test handling of company info errors."""
        mock_ticker.side_effect = Exception("yfinance error")
        
        result = yfinance_fetcher.get_company_info("RELIANCE")
        
        assert result is None
    
    @patch('data_sources.yfinance_fetcher.time.sleep')
    @patch('data_sources.yfinance_fetcher.YFinanceFetcher.get_historical_data')
    def test_batch_fetch_historical_data(self, mock_get_data, mock_sleep, yfinance_fetcher, sample_ohlcv_data):
        """Test batch fetching of historical data."""
        # Mock get_historical_data to return sample data
        mock_get_data.return_value = sample_ohlcv_data
        
        symbols = ["RELIANCE", "TCS", "HDFCBANK"]
        results = yfinance_fetcher.batch_fetch_historical_data(
            symbols=symbols,
            period="1mo",
            batch_size=2,
            delay_between_batches=0.1
        )
        
        assert len(results) == 3
        assert all(symbol in results for symbol in symbols)
        assert all(results[symbol] is not None for symbol in symbols)
        # Should have delays between batches
        assert mock_sleep.call_count >= 1
    
    @patch('data_sources.yfinance_fetcher.time.sleep')
    @patch('data_sources.yfinance_fetcher.YFinanceFetcher.get_historical_data')
    def test_batch_fetch_handles_failures(self, mock_get_data, mock_sleep, yfinance_fetcher):
        """Test batch fetching handles individual failures."""
        # Mock some failures
        def side_effect(symbol, **kwargs):
            if symbol == "FAIL":
                return None
            return pd.DataFrame({'date': [date.today()], 'open': [100], 'high': [105], 
                               'low': [99], 'close': [103], 'volume': [1000000]})
        
        mock_get_data.side_effect = side_effect
        
        symbols = ["RELIANCE", "FAIL", "TCS"]
        results = yfinance_fetcher.batch_fetch_historical_data(symbols=symbols, batch_size=2)
        
        assert len(results) == 3
        assert results["RELIANCE"] is not None
        assert results["FAIL"] is None
        assert results["TCS"] is not None
