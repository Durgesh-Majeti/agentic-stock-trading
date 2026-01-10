"""Market data repository."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
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
        """Add or update daily market data."""
        existing = self.session.query(MarketDataDaily).filter(
            MarketDataDaily.stock_id == stock_id,
            MarketDataDaily.date == date
        ).first()
        
        if existing:
            # Update existing record
            for key, value in indicators.items():
                if hasattr(existing, key):
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
