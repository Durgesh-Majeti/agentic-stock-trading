"""Comprehensive unit tests for TechnicalIndicators."""
import pytest
import pandas as pd
import numpy as np
from utils.technical_indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Test cases for TechnicalIndicators."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # Generate realistic price data
        base_price = 100.0
        prices = []
        for i in range(100):
            change = np.random.normal(0, 2)
            base_price = max(50, base_price + change)
            prices.append(base_price)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000000, 5000000) for _ in range(100)]
        })
        return df
    
    def test_calculate_all_indicators(self, sample_data):
        """Test calculating all indicators."""
        indicators = TechnicalIndicators.calculate_all_indicators(sample_data)
        
        assert isinstance(indicators, dict)
        assert 'rsi' in indicators
        assert 'macd' in indicators
        assert 'bollinger_upper' in indicators
        assert 'sma_20' in indicators
        assert 'ema_12' in indicators
    
    def test_calculate_all_indicators_empty(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        indicators = TechnicalIndicators.calculate_all_indicators(df)
        assert indicators == {}
    
    def test_calculate_all_indicators_insufficient_data(self):
        """Test with insufficient data."""
        df = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000] * 10
        })
        indicators = TechnicalIndicators.calculate_all_indicators(df)
        assert indicators == {}
    
    def test_calculate_rsi(self, sample_data):
        """Test RSI calculation."""
        rsi = TechnicalIndicators._calculate_rsi(sample_data['close'])
        assert rsi is not None
        assert 0 <= rsi <= 100
    
    def test_calculate_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        close = pd.Series([100] * 10)
        rsi = TechnicalIndicators._calculate_rsi(close)
        assert rsi is None
    
    def test_calculate_macd(self, sample_data):
        """Test MACD calculation."""
        macd_data = TechnicalIndicators._calculate_macd(sample_data['close'])
        assert 'macd' in macd_data
        assert 'macd_signal' in macd_data
        assert 'macd_histogram' in macd_data
    
    def test_calculate_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation."""
        bb_data = TechnicalIndicators._calculate_bollinger_bands(sample_data['close'])
        assert 'bollinger_upper' in bb_data
        assert 'bollinger_lower' in bb_data
        assert 'bollinger_middle' in bb_data
        assert bb_data['bollinger_upper'] > bb_data['bollinger_middle']
        assert bb_data['bollinger_lower'] < bb_data['bollinger_middle']
    
    def test_calculate_adx(self, sample_data):
        """Test ADX calculation."""
        adx_data = TechnicalIndicators._calculate_adx(
            sample_data['high'], sample_data['low'], sample_data['close']
        )
        assert 'adx' in adx_data
        assert 'adx_positive' in adx_data
        assert 'adx_negative' in adx_data
    
    def test_calculate_stochastic(self, sample_data):
        """Test Stochastic calculation."""
        stoch_data = TechnicalIndicators._calculate_stochastic(
            sample_data['high'], sample_data['low'], sample_data['close']
        )
        assert 'stochastic_k' in stoch_data
        assert 'stochastic_d' in stoch_data
        assert 0 <= stoch_data['stochastic_k'] <= 100
    
    def test_calculate_williams_r(self, sample_data):
        """Test Williams %R calculation."""
        williams_r = TechnicalIndicators._calculate_williams_r(
            sample_data['high'], sample_data['low'], sample_data['close']
        )
        assert williams_r is not None
        assert -100 <= williams_r <= 0
    
    def test_calculate_cci(self, sample_data):
        """Test CCI calculation."""
        cci = TechnicalIndicators._calculate_cci(
            sample_data['high'], sample_data['low'], sample_data['close']
        )
        assert cci is not None
    
    def test_calculate_atr(self, sample_data):
        """Test ATR calculation."""
        atr = TechnicalIndicators._calculate_atr(
            sample_data['high'], sample_data['low'], sample_data['close']
        )
        assert atr is not None
        assert atr > 0
    
    def test_calculate_obv(self, sample_data):
        """Test OBV calculation."""
        obv = TechnicalIndicators._calculate_obv(sample_data['close'], sample_data['volume'])
        assert obv is not None
    
    def test_calculate_all_indicators_vectorized(self, sample_data):
        """Test vectorized indicator calculation."""
        result_df = TechnicalIndicators.calculate_all_indicators_vectorized(sample_data)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'rsi' in result_df.columns
        assert 'macd' in result_df.columns
        assert 'bollinger_upper' in result_df.columns
        assert len(result_df) == len(sample_data)
    
    def test_calculate_all_indicators_vectorized_empty(self):
        """Test vectorized calculation with empty DataFrame."""
        df = pd.DataFrame()
        result = TechnicalIndicators.calculate_all_indicators_vectorized(df)
        assert 'rsi' in result.columns
        assert len(result) == 0
    
    def test_calculate_all_indicators_vectorized_insufficient(self):
        """Test vectorized calculation with insufficient data."""
        df = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000] * 10
        })
        result = TechnicalIndicators.calculate_all_indicators_vectorized(df)
        assert 'rsi' in result.columns
        assert result['rsi'].iloc[-1] is None or pd.isna(result['rsi'].iloc[-1])
    
    def test_indicators_no_nan_values(self, sample_data):
        """Test that indicators don't contain NaN (converted to None)."""
        indicators = TechnicalIndicators.calculate_all_indicators(sample_data)
        
        for key, value in indicators.items():
            if value is not None:
                assert not pd.isna(value), f"{key} should not be NaN"
    
    def test_vectorized_vs_row_by_row_consistency(self, sample_data):
        """Test that vectorized and row-by-row give similar results."""
        # Get last row indicators from vectorized
        vectorized_df = TechnicalIndicators.calculate_all_indicators_vectorized(sample_data)
        vectorized_rsi = vectorized_df['rsi'].iloc[-1]
        
        # Get from row-by-row
        row_by_row = TechnicalIndicators.calculate_all_indicators(sample_data)
        row_by_row_rsi = row_by_row.get('rsi')
        
        # Should be similar (within small tolerance)
        if vectorized_rsi is not None and row_by_row_rsi is not None:
            assert abs(vectorized_rsi - row_by_row_rsi) < 1.0  # Small tolerance for rounding
