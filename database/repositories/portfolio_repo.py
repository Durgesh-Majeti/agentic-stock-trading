"""Portfolio repository."""
from sqlalchemy.orm import Session
from typing import List, Optional
from database.models import Portfolio, Stock


class PortfolioRepository:
    """Repository for portfolio operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_portfolio(self) -> List[Portfolio]:
        """Get all portfolio holdings."""
        return self.session.query(Portfolio).filter(
            Portfolio.quantity > 0
        ).all()
    
    def get_holding(self, stock_id: int) -> Optional[Portfolio]:
        """Get holding for a specific stock."""
        return self.session.query(Portfolio).filter(
            Portfolio.stock_id == stock_id
        ).first()
    
    def add_or_update_holding(
        self,
        stock_id: int,
        quantity: int,
        price: float,
        current_price: float
    ) -> Portfolio:
        """Add or update portfolio holding."""
        holding = self.get_holding(stock_id)
        
        if holding:
            # Update existing holding
            total_cost = (holding.avg_price * holding.quantity) + (price * quantity)
            total_quantity = holding.quantity + quantity
            holding.avg_price = total_cost / total_quantity if total_quantity > 0 else price
            holding.quantity = total_quantity
            holding.current_price = current_price
            holding.unrealized_pnl = (current_price - holding.avg_price) * holding.quantity
        else:
            # Create new holding
            holding = Portfolio(
                stock_id=stock_id,
                quantity=quantity,
                avg_price=price,
                current_price=current_price,
                unrealized_pnl=(current_price - price) * quantity
            )
            self.session.add(holding)
        
        self.session.commit()
        self.session.refresh(holding)
        return holding
    
    def reduce_holding(
        self,
        stock_id: int,
        quantity: int,
        exit_price: float
    ) -> tuple[Optional[Portfolio], float]:
        """Reduce holding and calculate realized P&L."""
        holding = self.get_holding(stock_id)
        
        if not holding or holding.quantity < quantity:
            return None, 0.0
        
        # Calculate realized P&L
        realized_pnl = (exit_price - holding.avg_price) * quantity
        holding.realized_pnl += realized_pnl
        holding.quantity -= quantity
        
        if holding.quantity == 0:
            self.session.delete(holding)
            holding = None
        else:
            holding.current_price = exit_price
            holding.unrealized_pnl = (exit_price - holding.avg_price) * holding.quantity
        
        self.session.commit()
        if holding:
            self.session.refresh(holding)
        
        return holding, realized_pnl
    
    def update_current_prices(self, stock_id: int, current_price: float):
        """Update current price for a holding."""
        holding = self.get_holding(stock_id)
        if holding:
            holding.current_price = current_price
            holding.unrealized_pnl = (current_price - holding.avg_price) * holding.quantity
            self.session.commit()
    
    def get_total_portfolio_value(self) -> float:
        """Get total portfolio value."""
        holdings = self.get_portfolio()
        return sum(h.current_price * h.quantity for h in holdings)
    
    def get_total_pnl(self) -> tuple[float, float]:
        """Get total realized and unrealized P&L."""
        holdings = self.get_portfolio()
        realized = sum(h.realized_pnl for h in holdings)
        unrealized = sum(h.unrealized_pnl for h in holdings)
        return realized, unrealized
