"""Technical indicators calculation (29 indicators)."""
import pandas as pd
import numpy as np
from typing import Dict, Optional


class TechnicalIndicators:
    """Calculate 29 technical indicators for market data."""
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate all 29 technical indicators.
        
        Args:
            df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            
        Returns:
            Dictionary with all indicator values
        """
        if df.empty or len(df) < 20:
            return {}
        
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        indicators = {}
        
        # RSI (Relative Strength Index)
        indicators['rsi'] = TechnicalIndicators._calculate_rsi(close)
        
        # MACD
        macd_data = TechnicalIndicators._calculate_macd(close)
        indicators.update(macd_data)
        
        # Bollinger Bands
        bb_data = TechnicalIndicators._calculate_bollinger_bands(close)
        indicators.update(bb_data)
        
        # Moving Averages
        indicators['sma_20'] = close.rolling(20).mean().iloc[-1]
        indicators['sma_50'] = close.rolling(50).mean().iloc[-1]
        indicators['sma_200'] = close.rolling(200).mean().iloc[-1]
        indicators['ema_12'] = close.ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = close.ewm(span=26).mean().iloc[-1]
        
        # ADX
        adx_data = TechnicalIndicators._calculate_adx(high, low, close)
        indicators.update(adx_data)
        
        # Stochastic
        stoch_data = TechnicalIndicators._calculate_stochastic(high, low, close)
        indicators.update(stoch_data)
        
        # Williams %R
        indicators['williams_r'] = TechnicalIndicators._calculate_williams_r(high, low, close)
        
        # CCI
        indicators['cci'] = TechnicalIndicators._calculate_cci(high, low, close)
        
        # ATR
        indicators['atr'] = TechnicalIndicators._calculate_atr(high, low, close)
        
        # OBV
        indicators['obv'] = TechnicalIndicators._calculate_obv(close, volume)
        
        # Volume indicators
        indicators['volume_sma'] = volume.rolling(20).mean().iloc[-1]
        indicators['volume_ratio'] = volume.iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 0
        
        # Price change
        indicators['price_change'] = close.iloc[-1] - close.iloc[-2] if len(close) > 1 else 0
        indicators['price_change_percent'] = (indicators['price_change'] / close.iloc[-2] * 100) if len(close) > 1 and close.iloc[-2] > 0 else 0
        
        # High-Low Range
        indicators['high_low_range'] = high.iloc[-1] - low.iloc[-1]
        indicators['high_low_range_percent'] = (indicators['high_low_range'] / low.iloc[-1] * 100) if low.iloc[-1] > 0 else 0
        
        # Momentum
        indicators['momentum'] = close.iloc[-1] - close.iloc[-10] if len(close) > 10 else 0
        
        # ROC (Rate of Change)
        indicators['roc'] = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10] * 100) if len(close) > 10 and close.iloc[-10] > 0 else 0
        
        # Convert NaN to None
        return {k: (v if not pd.isna(v) else None) for k, v in indicators.items()}
    
    @staticmethod
    def _calculate_rsi(close: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI."""
        if len(close) < period + 1:
            return None
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    @staticmethod
    def _calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD."""
        if len(close) < slow:
            return {'macd': None, 'macd_signal': None, 'macd_histogram': None}
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return {
            'macd': macd.iloc[-1],
            'macd_signal': macd_signal.iloc[-1],
            'macd_histogram': macd_histogram.iloc[-1]
        }
    
    @staticmethod
    def _calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        if len(close) < period:
            return {'bollinger_upper': None, 'bollinger_lower': None, 'bollinger_middle': None}
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        return {
            'bollinger_upper': (sma + std * std_dev).iloc[-1],
            'bollinger_lower': (sma - std * std_dev).iloc[-1],
            'bollinger_middle': sma.iloc[-1]
        }
    
    @staticmethod
    def _calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Dict[str, float]:
        """Calculate ADX (simplified version)."""
        if len(close) < period * 2:
            return {'adx': None, 'adx_positive': None, 'adx_negative': None}
        # Simplified ADX calculation
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = TechnicalIndicators._calculate_atr(high, low, close, period)
        if tr is None or tr == 0:
            return {'adx': None, 'adx_positive': None, 'adx_negative': None}
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return {
            'adx': adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else None,
            'adx_positive': plus_di.iloc[-1] if not pd.isna(plus_di.iloc[-1]) else None,
            'adx_negative': minus_di.iloc[-1] if not pd.isna(minus_di.iloc[-1]) else None
        }
    
    @staticmethod
    def _calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        """Calculate Stochastic Oscillator."""
        if len(close) < k_period:
            return {'stochastic_k': None, 'stochastic_d': None}
        lowest_low = low.rolling(k_period).min()
        highest_high = high.rolling(k_period).max()
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(d_period).mean()
        return {
            'stochastic_k': k.iloc[-1] if not pd.isna(k.iloc[-1]) else None,
            'stochastic_d': d.iloc[-1] if not pd.isna(d.iloc[-1]) else None
        }
    
    @staticmethod
    def _calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Williams %R."""
        if len(close) < period:
            return None
        highest_high = high.rolling(period).max()
        lowest_low = low.rolling(period).min()
        wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return wr.iloc[-1] if not pd.isna(wr.iloc[-1]) else None
    
    @staticmethod
    def _calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> Optional[float]:
        """Calculate Commodity Channel Index."""
        if len(close) < period:
            return None
        tp = (high + low + close) / 3
        sma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma) / (0.015 * mad)
        return cci.iloc[-1] if not pd.isna(cci.iloc[-1]) else None
    
    @staticmethod
    def _calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Average True Range."""
        if len(close) < period + 1:
            return None
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else None
    
    @staticmethod
    def _calculate_obv(close: pd.Series, volume: pd.Series) -> Optional[float]:
        """Calculate On-Balance Volume."""
        if len(close) < 2:
            return None
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv.iloc[-1]
