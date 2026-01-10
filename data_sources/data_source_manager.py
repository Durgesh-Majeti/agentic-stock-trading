"""Data source orchestrator - manages multiple data sources with fallback."""
from typing import Optional, Dict, List
from datetime import datetime, date, timedelta
from loguru import logger
from data_sources.yfinance_fetcher import YFinanceFetcher
import pandas as pd


class DataSourceManager:
    """Manages data sources with primary/backup selection and fallback logic.
    
    Current implementation: yfinance only (Shoonya/Upstox to be added later)
    """
    
    def __init__(self):
        """Initialize data source manager."""
        self.yfinance_fetcher = YFinanceFetcher()
        self.primary_source = "yfinance"  # Will be "shoonya" when integrated
        self.backup_source = "yfinance"
        self.data_freshness_threshold = timedelta(minutes=2)  # 2 minutes
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "2y"
    ) -> Optional[pd.DataFrame]:
        """Get historical data with fallback logic.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (optional)
            end_date: End date (optional)
            period: Period string if dates not provided (default: "2y")
            
        Returns:
            DataFrame with OHLCV data, or None if all sources fail
        """
        # For now, only yfinance is available
        # TODO: Add Shoonya as primary, Upstox as backup when integrated
        
        try:
            logger.debug(f"Fetching historical data for {symbol} from yfinance...")
            df = self.yfinance_fetcher.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            
            if df is not None and not df.empty:
                logger.debug(f"Successfully fetched {len(df)} rows for {symbol}")
                return df
            else:
                logger.warning(f"No data returned from yfinance for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_latest_price(
        self,
        symbol: str,
        max_age: Optional[timedelta] = None
    ) -> Optional[Dict]:
        """Get latest price for a symbol.
        
        Args:
            symbol: Stock symbol
            max_age: Maximum age of data (default: 2 minutes)
            
        Returns:
            Dictionary with price data, or None if unavailable
        """
        if max_age is None:
            max_age = self.data_freshness_threshold
        
        try:
            # Fetch recent data (last 5 days to get latest)
            df = self.get_historical_data(symbol, period="5d")
            
            if df is None or df.empty:
                return None
            
            # Get latest row
            latest = df.iloc[-1]
            
            # Check data freshness
            if 'date' in latest:
                data_date = latest['date']
                if isinstance(data_date, str):
                    data_date = pd.to_datetime(data_date).date()
                
                age = date.today() - data_date
                if age > timedelta(days=1):
                    logger.warning(f"Data for {symbol} is {age.days} days old")
            
            return {
                'symbol': symbol,
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'close': float(latest['close']),
                'volume': int(latest['volume']),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
    
    def validate_data_freshness(
        self,
        timestamp: datetime,
        max_age: Optional[timedelta] = None
    ) -> bool:
        """Validate if data is fresh enough.
        
        Args:
            timestamp: Data timestamp
            max_age: Maximum age threshold (default: 2 minutes)
            
        Returns:
            True if data is fresh, False otherwise
        """
        if max_age is None:
            max_age = self.data_freshness_threshold
        
        age = datetime.now() - timestamp
        return age <= max_age
    
    def batch_get_historical_data(
        self,
        symbols: List[str],
        period: str = "2y",
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """Get historical data for multiple symbols in batches.
        
        Args:
            symbols: List of stock symbols
            period: Period string (e.g., "2y")
            batch_size: Number of symbols per batch
            delay_between_batches: Delay in seconds between batches
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        return self.yfinance_fetcher.batch_fetch_historical_data(
            symbols=symbols,
            period=period,
            batch_size=batch_size,
            delay_between_batches=delay_between_batches
        )
    
    def get_nifty_500_symbols(self) -> List[Dict[str, str]]:
        """Get Nifty 500 symbol list.
        
        Returns:
            List of dictionaries with symbol, name, and sector
        """
        return self.yfinance_fetcher.get_nifty_500_symbols()
    
    # TODO: Add these methods when Shoonya/Upstox are integrated
    # def get_realtime_quote(self, symbol: str) -> Optional[Dict]:
    #     """Get real-time quote from primary source (Shoonya)."""
    #     pass
    #
    # def place_order(self, order_data: Dict) -> Optional[Dict]:
    #     """Place order via primary source (Shoonya)."""
    #     pass
