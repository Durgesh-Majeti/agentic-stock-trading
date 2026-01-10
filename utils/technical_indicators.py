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
    
    @staticmethod
    def calculate_all_indicators_vectorized(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all 29 technical indicators for entire DataFrame (vectorized).
        
        This is much faster than row-by-row calculation - calculates all indicators
        for all rows at once using vectorized pandas operations.
        
        Args:
            df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            
        Returns:
            DataFrame with added indicator columns
        """
        if df.empty or len(df) < 20:
            # Initialize empty indicator columns
            indicator_cols = [
                'rsi', 'macd', 'macd_signal', 'macd_histogram',
                'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
                'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_20', 'ema_50',
                'adx', 'adx_positive', 'adx_negative',
                'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv', 'mfi',
                'volume_sma', 'price_change', 'price_change_percent',
                'high_low_range', 'high_low_range_percent', 'volume_ratio',
                'momentum', 'roc'
            ]
            for col in indicator_cols:
                if col not in df.columns:
                    df[col] = None
            return df
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return df
        
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # RSI (vectorized)
        if len(close) >= 15:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        else:
            df['rsi'] = None
        
        # MACD (vectorized)
        if len(close) >= 26:
            ema_fast = close.ewm(span=12).mean()
            ema_slow = close.ewm(span=26).mean()
            df['macd'] = ema_fast - ema_slow
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
        else:
            df['macd'] = None
            df['macd_signal'] = None
            df['macd_histogram'] = None
        
        # Bollinger Bands (vectorized)
        if len(close) >= 20:
            sma = close.rolling(20).mean()
            std = close.rolling(20).std()
            df['bollinger_middle'] = sma
            df['bollinger_upper'] = sma + std * 2
            df['bollinger_lower'] = sma - std * 2
        else:
            df['bollinger_upper'] = None
            df['bollinger_lower'] = None
            df['bollinger_middle'] = None
        
        # Moving Averages (vectorized)
        df['sma_20'] = close.rolling(20).mean()
        df['sma_50'] = close.rolling(50).mean()
        df['sma_200'] = close.rolling(200).mean()
        df['ema_12'] = close.ewm(span=12).mean()
        df['ema_26'] = close.ewm(span=26).mean()
        df['ema_20'] = close.ewm(span=20).mean()
        df['ema_50'] = close.ewm(span=50).mean()
        
        # ADX (vectorized - simplified)
        if len(close) >= 28:
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            # ATR for ADX calculation
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            
            plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            df['adx'] = dx.rolling(14).mean()
            df['adx_positive'] = plus_di
            df['adx_negative'] = minus_di
        else:
            df['adx'] = None
            df['adx_positive'] = None
            df['adx_negative'] = None
        
        # Stochastic (vectorized)
        if len(close) >= 14:
            lowest_low = low.rolling(14).min()
            highest_high = high.rolling(14).max()
            df['stochastic_k'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            df['stochastic_d'] = df['stochastic_k'].rolling(3).mean()
        else:
            df['stochastic_k'] = None
            df['stochastic_d'] = None
        
        # Williams %R (vectorized)
        if len(close) >= 14:
            highest_high = high.rolling(14).max()
            lowest_low = low.rolling(14).min()
            df['williams_r'] = -100 * ((highest_high - close) / (highest_high - lowest_low))
        else:
            df['williams_r'] = None
        
        # CCI (vectorized)
        if len(close) >= 20:
            tp = (high + low + close) / 3
            sma = tp.rolling(20).mean()
            mad = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=False)
            df['cci'] = (tp - sma) / (0.015 * mad)
        else:
            df['cci'] = None
        
        # ATR (vectorized)
        if len(close) >= 15:
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = tr.rolling(14).mean()
        else:
            df['atr'] = None
        
        # OBV (vectorized)
        if len(close) >= 2:
            df['obv'] = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        else:
            df['obv'] = None
        
        # MFI (Money Flow Index) - vectorized
        if len(close) >= 14:
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            price_change = typical_price.diff()
            positive_flow = money_flow.where(price_change > 0, 0).rolling(14).sum()
            negative_flow = money_flow.where(price_change < 0, 0).rolling(14).sum()
            # Avoid division by zero
            mfi_ratio = positive_flow / negative_flow.replace(0, np.nan)
            df['mfi'] = 100 - (100 / (1 + mfi_ratio))
            df['mfi'] = df['mfi'].replace([np.inf, -np.inf, np.nan], None)
        else:
            df['mfi'] = None
        
        # Volume indicators (vectorized)
        df['volume_sma'] = volume.rolling(20).mean()
        df['volume_ratio'] = volume / df['volume_sma']
        df['volume_ratio'] = df['volume_ratio'].replace([np.inf, -np.inf], 0)
        
        # Price change (vectorized)
        df['price_change'] = close.diff()
        df['price_change_percent'] = (df['price_change'] / close.shift()) * 100
        df['price_change_percent'] = df['price_change_percent'].replace([np.inf, -np.inf], 0)
        
        # High-Low Range (vectorized)
        df['high_low_range'] = high - low
        df['high_low_range_percent'] = (df['high_low_range'] / low) * 100
        df['high_low_range_percent'] = df['high_low_range_percent'].replace([np.inf, -np.inf], 0)
        
        # Momentum (vectorized)
        df['momentum'] = close.diff(10)
        
        # ROC (vectorized)
        df['roc'] = ((close - close.shift(10)) / close.shift(10)) * 100
        df['roc'] = df['roc'].replace([np.inf, -np.inf], 0)
        
        # Replace NaN with None for database compatibility
        indicator_cols = [
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'adx', 'adx_positive', 'adx_negative',
            'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv',
            'volume_sma', 'price_change', 'price_change_percent',
            'high_low_range', 'high_low_range_percent', 'volume_ratio',
            'momentum', 'roc'
        ]
        for col in indicator_cols:
            if col in df.columns:
                df[col] = df[col].where(pd.notna(df[col]), None)
        
        return df