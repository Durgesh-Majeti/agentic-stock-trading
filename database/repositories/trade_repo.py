"""Trade repository."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from database.models import Trade
from config.constants import OrderType, TradeStatus


class TradeRepository:
    """Repository for trade operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_trade(
        self,
        stock_id: int,
        order_id: Optional[int],
        buy_sell: OrderType,
        quantity: int,
        entry_price: float,
        stop_loss: float,
        target: float
    ) -> Trade:
        """Create a new trade."""
        trade = Trade(
            stock_id=stock_id,
            order_id=order_id,
            buy_sell=buy_sell,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            status=TradeStatus.OPEN,
            executed_at=datetime.utcnow()
        )
        self.session.add(trade)
        self.session.commit()
        self.session.refresh(trade)
        return trade
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades."""
        return self.session.query(Trade).filter(
            Trade.status == TradeStatus.OPEN
        ).all()
    
    def get_trade(self, trade_id: int) -> Optional[Trade]:
        """Get trade by ID."""
        return self.session.query(Trade).filter(Trade.id == trade_id).first()
    
    def close_trade(
        self,
        trade_id: int,
        exit_price: float,
        status: TradeStatus = TradeStatus.CLOSED
    ) -> Optional[Trade]:
        """Close a trade."""
        trade = self.get_trade(trade_id)
        if trade and trade.status == TradeStatus.OPEN:
            trade.exit_price = exit_price
            trade.status = status
            trade.closed_at = datetime.utcnow()
            
            # Calculate P&L
            if trade.buy_sell == OrderType.BUY:
                trade.pnl = (exit_price - trade.entry_price) * trade.quantity
            else:  # SELL
                trade.pnl = (trade.entry_price - exit_price) * trade.quantity
            
            trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
            
            self.session.commit()
            self.session.refresh(trade)
        return trade
    
    def get_recent_trades(self, limit: int = 100) -> List[Trade]:
        """Get recent trades."""
        return self.session.query(Trade).order_by(
            desc(Trade.created_at)
        ).limit(limit).all()
    
    def get_trades_by_stock(self, stock_id: int) -> List[Trade]:
        """Get all trades for a stock."""
        return self.session.query(Trade).filter(
            Trade.stock_id == stock_id
        ).order_by(desc(Trade.created_at)).all()
