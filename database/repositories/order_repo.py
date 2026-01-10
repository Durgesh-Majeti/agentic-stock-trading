"""Order repository."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from database.models import Order
from config.constants import OrderStatus, OrderType


class OrderRepository:
    """Repository for order operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_order(
        self,
        stock_id: int,
        order_type: OrderType,
        quantity: int,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        confidence_score: float,
        price: Optional[float] = None
    ) -> Order:
        """Create a new order (pending approval)."""
        order = Order(
            stock_id=stock_id,
            order_type=order_type,
            quantity=quantity,
            price=price,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            confidence_score=confidence_score,
            order_status=OrderStatus.PENDING_APPROVAL
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending approval orders."""
        return self.session.query(Order).filter(
            Order.order_status == OrderStatus.PENDING_APPROVAL
        ).order_by(desc(Order.created_at)).all()
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID."""
        return self.session.query(Order).filter(Order.id == order_id).first()
    
    def approve_order(self, order_id: int) -> Optional[Order]:
        """Approve an order."""
        order = self.get_order(order_id)
        if order and order.order_status == OrderStatus.PENDING_APPROVAL:
            order.order_status = OrderStatus.APPROVED
            order.approved_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(order)
        return order
    
    def reject_order(self, order_id: int) -> Optional[Order]:
        """Reject an order."""
        order = self.get_order(order_id)
        if order and order.order_status == OrderStatus.PENDING_APPROVAL:
            order.order_status = OrderStatus.REJECTED
            order.rejected_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(order)
        return order
    
    def mark_executed(
        self,
        order_id: int,
        executed_price: float,
        execution_message: Optional[str] = None
    ) -> Optional[Order]:
        """Mark order as executed."""
        order = self.get_order(order_id)
        if order:
            order.order_status = OrderStatus.EXECUTED
            order.executed_at = datetime.utcnow()
            order.executed_price = executed_price
            order.execution_message = execution_message
            self.session.commit()
            self.session.refresh(order)
        return order
    
    def mark_failed(self, order_id: int, error_message: str) -> Optional[Order]:
        """Mark order as failed."""
        order = self.get_order(order_id)
        if order:
            order.order_status = OrderStatus.FAILED
            order.execution_message = error_message
            self.session.commit()
            self.session.refresh(order)
        return order
    
    def get_recent_orders(self, limit: int = 50) -> List[Order]:
        """Get recent orders."""
        return self.session.query(Order).order_by(
            desc(Order.created_at)
        ).limit(limit).all()
