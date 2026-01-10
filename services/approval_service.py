"""Approval service for managing trade approvals."""
from typing import Optional
from database.repositories.order_repo import OrderRepository
from database.repositories.user_action_repo import UserActionRepository
from loguru import logger


class ApprovalService:
    """Service for managing order approvals."""
    
    def __init__(self, order_repo: OrderRepository, user_action_repo: UserActionRepository):
        self.order_repo = order_repo
        self.user_action_repo = user_action_repo
    
    def get_pending_approvals(self):
        """Get all pending approval orders."""
        return self.order_repo.get_pending_orders()
    
    def approve_order(self, order_id: int, user_id: Optional[str] = None) -> bool:
        """Approve an order.
        
        Args:
            order_id: Order ID to approve
            user_id: User ID who approved (e.g., Telegram user ID)
            
        Returns:
            True if approved successfully, False otherwise
        """
        order = self.order_repo.approve_order(order_id)
        if order:
            # Log user action
            self.user_action_repo.log_action(
                action_type="APPROVE_ORDER",
                details={"order_id": order_id, "stock_id": order.stock_id},
                user_id=user_id
            )
            logger.info(f"Order {order_id} approved by user {user_id}")
            return True
        return False
    
    def reject_order(self, order_id: int, user_id: Optional[str] = None) -> bool:
        """Reject an order.
        
        Args:
            order_id: Order ID to reject
            user_id: User ID who rejected
            
        Returns:
            True if rejected successfully, False otherwise
        """
        order = self.order_repo.reject_order(order_id)
        if order:
            # Log user action
            self.user_action_repo.log_action(
                action_type="REJECT_ORDER",
                details={"order_id": order_id, "stock_id": order.stock_id},
                user_id=user_id
            )
            logger.info(f"Order {order_id} rejected by user {user_id}")
            return True
        return False
