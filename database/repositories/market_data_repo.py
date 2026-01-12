"""Market data repository."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from loguru import logger
from database.models import Stock, MarketDataDaily, MarketDataIntraday
from config.constants import DAILY_DATA_RETENTION_DAYS, INTRADAY_DATA_RETENTION_DAYS


class MarketDataRepository:
    """Repository for market data operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_stock_by_symbol(self, symbol: str, exchange: str = "NSE") -> Optional[Stock]:
        """Get stock by symbol."""
        return self.session.query(Stock).filter(
            Stock.symbol == symbol.upper(),
            Stock.exchange == exchange
        ).first()
    
    def create_stock(
        self, 
        symbol: str, 
        name: str, 
        exchange: str = "NSE",
        sector: Optional[str] = None,
        market_cap: Optional[float] = None
    ) -> Stock:
        """Create or get stock.
        
        Args:
            symbol: Stock symbol (e.g., "TCS-EQ")
            name: Company name
            exchange: Exchange code (default: "NSE")
            sector: Sector name (optional)
            market_cap: Market capitalization in rupees (optional)
            
        Returns:
            Stock object
        """
        stock = self.get_stock_by_symbol(symbol, exchange)
        if not stock:
            stock = Stock(
                symbol=symbol.upper(), 
                name=name, 
                exchange=exchange,
                sector=sector,
                market_cap=market_cap
            )
            self.session.add(stock)
            self.session.commit()
            self.session.refresh(stock)
        else:
            # Update sector and market_cap if provided and different
            updated = False
            if sector is not None and stock.sector != sector:
                stock.sector = sector
                updated = True
            if market_cap is not None and stock.market_cap != market_cap:
                stock.market_cap = market_cap
                updated = True
            if updated:
                self.session.commit()
                self.session.refresh(stock)
        return stock
    
    def update_stock_info(
        self,
        stock_id: int,
        sector: Optional[str] = None,
        market_cap: Optional[float] = None
    ) -> Optional[Stock]:
        """Update stock sector and/or market cap.
        
        Args:
            stock_id: Stock ID
            sector: Sector name (optional)
            market_cap: Market capitalization in rupees (optional)
            
        Returns:
            Updated Stock object, or None if stock not found
        """
        stock = self.session.query(Stock).filter(Stock.id == stock_id).first()
        if not stock:
            return None
        
        if sector is not None:
            stock.sector = sector
        if market_cap is not None:
            stock.market_cap = market_cap
        
        self.session.commit()
        self.session.refresh(stock)
        return stock
    
    def _validate_market_data(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int
    ) -> bool:
        """
        Validate market data quality.
        
        Args:
            open: Opening price
            high: High price
            low: Low price
            close: Closing price
            volume: Trading volume
        
        Returns:
            True if valid, False otherwise
        """
        # Price range validation (0 to 1 million rupees per share)
        max_price = 1000000.0
        min_price = 0.0
        
        # Check all prices are positive and within range
        for price_name, price_value in [("open", open), ("high", high), 
                                        ("low", low), ("close", close)]:
            if price_value < min_price or price_value > max_price:
                logger.error(
                    f"Invalid {price_name} price: {price_value} "
                    f"(must be between {min_price} and {max_price})"
                )
                return False
        
        # High must be >= Low
        if high < low:
            logger.error(f"High price ({high}) must be >= Low price ({low})")
            return False
        
        # Open and Close must be within High-Low range
        if not (low <= open <= high):
            logger.error(
                f"Open price ({open}) must be within High-Low range "
                f"({low} to {high})"
            )
            return False
        
        if not (low <= close <= high):
            logger.error(
                f"Close price ({close}) must be within High-Low range "
                f"({low} to {high})"
            )
            return False
        
        # Volume must be non-negative
        if volume < 0:
            logger.error(f"Volume ({volume}) must be non-negative")
            return False
        
        return True
    
    def add_daily_data(
        self,
        stock_id: int,
        date: date,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        **indicators
    ) -> MarketDataDaily:
        """
        Add or update daily market data with validation.
        
        Args:
            stock_id: Stock ID
            date: Trading date
            open: Opening price
            high: High price
            low: Low price
            close: Closing price
            volume: Trading volume
            **indicators: Additional technical indicators
        
        Returns:
            MarketDataDaily object
        
        Raises:
            ValueError: If data validation fails
        """
        # Validate data quality before storage
        if not self._validate_market_data(open, high, low, close, volume):
            raise ValueError("Market data validation failed")
        
        existing = self.session.query(MarketDataDaily).filter(
            MarketDataDaily.stock_id == stock_id,
            MarketDataDaily.date == date
        ).first()
        
        if existing:
            # Update existing record
            for key, value in indicators.items():
                if hasattr(existing, key):
                    # Validate indicator values if they're prices
                    if key in ['rsi', 'macd', 'macd_signal', 'macd_histogram']:
                        # Technical indicators have specific ranges
                        if not isinstance(value, (int, float)):
                            logger.warning(f"Invalid indicator value type for {key}: {type(value)}")
                            continue
                    setattr(existing, key, value)
            existing.open = open
            existing.high = high
            existing.low = low
            existing.close = close
            existing.volume = volume
            self.session.commit()
            return existing
        else:
            # Create new record
            data = MarketDataDaily(
                stock_id=stock_id,
                date=date,
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume,
                **indicators
            )
            self.session.add(data)
            self.session.commit()
            self.session.refresh(data)
            return data
    
    def get_latest_daily_data(self, stock_id: int) -> Optional[MarketDataDaily]:
        """Get latest daily data for a stock."""
        return self.session.query(MarketDataDaily).filter(
            MarketDataDaily.stock_id == stock_id
        ).order_by(desc(MarketDataDaily.date)).first()
    
    def get_daily_data_range(
        self,
        stock_id: int,
        start_date: date,
        end_date: date
    ) -> List[MarketDataDaily]:
        """Get daily data for a date range."""
        return self.session.query(MarketDataDaily).filter(
            and_(
                MarketDataDaily.stock_id == stock_id,
                MarketDataDaily.date >= start_date,
                MarketDataDaily.date <= end_date
            )
        ).order_by(MarketDataDaily.date).all()
    
    def add_intraday_data(
        self,
        stock_id: int,
        timestamp: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        interval: str = "1h"
    ) -> MarketDataIntraday:
        """Add intraday market data."""
        data = MarketDataIntraday(
            stock_id=stock_id,
            timestamp=timestamp,
            interval=interval,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def get_latest_intraday_data(self, stock_id: int) -> Optional[MarketDataIntraday]:
        """Get latest intraday data for a stock."""
        return self.session.query(MarketDataIntraday).filter(
            MarketDataIntraday.stock_id == stock_id
        ).order_by(desc(MarketDataIntraday.timestamp)).first()
    
    def get_stocks_by_sector(self, sector: str) -> List[Stock]:
        """Get all stocks in a given sector.
        
        Args:
            sector: Sector name
            
        Returns:
            List of Stock objects
        """
        return self.session.query(Stock).filter(
            Stock.sector == sector,
            Stock.is_active == True
        ).all()
    
    def get_stocks_by_market_cap_range(
        self, 
        min_cap: Optional[float] = None,
        max_cap: Optional[float] = None
    ) -> List[Stock]:
        """Get stocks within a market cap range.
        
        Args:
            min_cap: Minimum market cap (optional)
            max_cap: Maximum market cap (optional)
            
        Returns:
            List of Stock objects
        """
        query = self.session.query(Stock).filter(Stock.is_active == True)
        
        if min_cap is not None:
            query = query.filter(Stock.market_cap >= min_cap)
        if max_cap is not None:
            query = query.filter(Stock.market_cap <= max_cap)
        
        return query.all()
    
    def cleanup_old_data(self):
        """Clean up old data beyond retention period."""
        # Clean daily data older than retention period
        cutoff_date = date.today() - timedelta(days=DAILY_DATA_RETENTION_DAYS)
        self.session.query(MarketDataDaily).filter(
            MarketDataDaily.date < cutoff_date
        ).delete()
        
        # Clean intraday data older than retention period
        cutoff_datetime = datetime.utcnow() - timedelta(days=INTRADAY_DATA_RETENTION_DAYS)
        self.session.query(MarketDataIntraday).filter(
            MarketDataIntraday.timestamp < cutoff_datetime
        ).delete()
        
        self.session.commit()
    
    def get_existing_dates_for_stock(self, stock_id: int) -> set:
        """Get set of existing dates for a stock (for bulk existence check).
        
        Args:
            stock_id: Stock ID
            
        Returns:
            Set of date objects
        """
        results = self.session.query(MarketDataDaily.date).filter(
            MarketDataDaily.stock_id == stock_id
        ).all()
        return {row[0] for row in results}
    
    def bulk_insert_daily_data(
        self,
        stock_id: int,
        data_list: List[dict]
    ) -> int:
        """Bulk insert daily market data (much faster than individual inserts).
        
        Args:
            stock_id: Stock ID
            data_list: List of dictionaries with date, open, high, low, close, volume, and indicators
            
        Returns:
            Number of rows inserted
        """
        if not data_list:
            return 0
        
        # Define all indicator fields to ensure consistency
        indicator_fields = [
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_20', 'ema_50',
            'adx', 'adx_positive', 'adx_negative',
            'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv', 'mfi',
            'volume_sma', 'price_change', 'price_change_percent',
            'high_low_range', 'high_low_range_percent', 'volume_ratio',
            'momentum', 'roc'
        ]
        
        # Prepare bulk insert mappings - ensure ALL fields are always present
        # This is critical: SQLAlchemy bulk_insert_mappings requires consistent keys
        mappings = []
        for data in data_list:
            # Always include all fields, even if None, to ensure consistent mapping
            mapping = {
                'stock_id': stock_id,
                'date': data['date'],
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
                'close': data['close'],
                'volume': data['volume'],
                # All indicators - explicitly set to None if missing
                'rsi': data.get('rsi'),
                'macd': data.get('macd'),
                'macd_signal': data.get('macd_signal'),
                'macd_histogram': data.get('macd_histogram'),
                'bollinger_upper': data.get('bollinger_upper'),
                'bollinger_lower': data.get('bollinger_lower'),
                'bollinger_middle': data.get('bollinger_middle'),
                'sma_20': data.get('sma_20'),
                'sma_50': data.get('sma_50'),
                'sma_200': data.get('sma_200'),
                'ema_12': data.get('ema_12'),
                'ema_26': data.get('ema_26'),
                'ema_20': data.get('ema_20'),
                'ema_50': data.get('ema_50'),
                'adx': data.get('adx'),
                'adx_positive': data.get('adx_positive'),
                'adx_negative': data.get('adx_negative'),
                'stochastic_k': data.get('stochastic_k'),
                'stochastic_d': data.get('stochastic_d'),
                'williams_r': data.get('williams_r'),
                'cci': data.get('cci'),
                'atr': data.get('atr'),
                'obv': data.get('obv'),
                'mfi': data.get('mfi'),
                'volume_sma': data.get('volume_sma'),
                'price_change': data.get('price_change'),
                'price_change_percent': data.get('price_change_percent'),
                'high_low_range': data.get('high_low_range'),
                'high_low_range_percent': data.get('high_low_range_percent'),
                'volume_ratio': data.get('volume_ratio'),
                'momentum': data.get('momentum'),
                'roc': data.get('roc')
            }
            mappings.append(mapping)
        
        # Process in smaller batches to avoid SQLite parameter limits
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(mappings), batch_size):
            batch = mappings[i:i + batch_size]
            try:
                self.session.bulk_insert_mappings(MarketDataDaily, batch)
                self.session.flush()  # Flush to database but don't commit yet
                total_inserted += len(batch)
            except Exception as e:
                # Rollback this batch
                try:
                    self.session.rollback()
                except:
                    pass
                # If bulk insert fails, try individual inserts for this batch
                for mapping in batch:
                    try:
                        record = MarketDataDaily(**mapping)
                        self.session.add(record)
                        self.session.flush()  # Flush each record
                        total_inserted += 1
                    except Exception as e2:
                        # Skip this record if it still fails
                        try:
                            self.session.rollback()
                        except:
                            pass
                        continue
        
        return total_inserted
    
    def bulk_update_daily_data(
        self,
        stock_id: int,
        data_list: List[dict]
    ) -> int:
        """Bulk update existing daily market data.
        
        Uses efficient batch updates - queries records in batches and updates them.
        This is faster than individual queries but avoids SQLite parameter issues.
        
        Args:
            stock_id: Stock ID
            data_list: List of dictionaries with date and fields to update
            
        Returns:
            Number of rows updated
        """
        if not data_list:
            return 0
        
        # Process in smaller batches to avoid SQLite issues
        batch_size = 50
        updated_count = 0
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            
            # Update each record individually (more reliable with SQLite)
            # But we batch the commits for better performance
            for data in batch:
                try:
                    # Query existing record
                    existing = self.session.query(MarketDataDaily).filter(
                        MarketDataDaily.stock_id == stock_id,
                        MarketDataDaily.date == data['date']
                    ).first()
                    
                    if existing:
                        # Update OHLCV
                        existing.open = data['open']
                        existing.high = data['high']
                        existing.low = data['low']
                        existing.close = data['close']
                        existing.volume = data['volume']
                        
                        # Update indicators
                        indicator_fields = [
                            'rsi', 'macd', 'macd_signal', 'macd_histogram',
                            'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
                            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_20', 'ema_50',
                            'adx', 'adx_positive', 'adx_negative',
                            'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv', 'mfi',
                            'volume_sma', 'price_change', 'price_change_percent',
                            'high_low_range', 'high_low_range_percent', 'volume_ratio',
                            'momentum', 'roc'
                        ]
                        for field in indicator_fields:
                            if field in data:
                                setattr(existing, field, data[field])
                        
                        updated_count += 1
                except Exception as e:
                    # Skip this record if there's an error
                    continue
            
            # Flush changes but don't commit - let context manager handle commit
            if updated_count > 0:
                try:
                    self.session.flush()
                except Exception as e:
                    try:
                        self.session.rollback()
                    except:
                        pass
        
        return updated_count