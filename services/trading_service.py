"""Trading service for order execution."""
from typing import Optional
from database.repositories.order_repo import OrderRepository
from database.repositories.trade_repo import TradeRepository
from database.repositories.portfolio_repo import PortfolioRepository
from config.constants import OrderType, OrderStatus
from loguru import logger


class TradingService:
    """Service for executing trades."""
    
    def __init__(
        self,
        order_repo: OrderRepository,
        trade_repo: TradeRepository,
        portfolio_repo: PortfolioRepository
    ):
        self.order_repo = order_repo
        self.trade_repo = trade_repo
        self.portfolio_repo = portfolio_repo
    
    def execute_approved_orders(self):
        """Execute all approved orders (to be called by orchestrator)."""
        # This will be implemented with Shoonya API integration
        # For now, placeholder
        pass
    
    def create_trade_from_order(self, order_id: int) -> Optional[int]:
        """Create a trade record from an executed order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Trade ID if created, None otherwise
        """
        order = self.order_repo.get_order(order_id)
        if not order or order.order_status != OrderStatus.APPROVED:
            return None
        
        trade = self.trade_repo.create_trade(
            stock_id=order.stock_id,
            order_id=order_id,
            buy_sell=order.order_type,
            quantity=order.quantity,
            entry_price=order.entry_price or order.executed_price,
            stop_loss=order.stop_loss,
            target=order.target_price
        )
        
        logger.info(f"Trade {trade.id} created from order {order_id}")
        return trade.id
