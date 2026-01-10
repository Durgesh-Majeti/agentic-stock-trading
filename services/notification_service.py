"""Notification service for Telegram notifications."""
from typing import Optional
from loguru import logger


class NotificationService:
    """Service for sending notifications (Telegram, etc.)."""
    
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot
    
    def notify_new_order(self, order_id: int, order_details: dict):
        """Notify about new order requiring approval.
        
        Args:
            order_id: Order ID
            order_details: Order details dictionary
        """
        if self.telegram_bot:
            # Format message
            message = self._format_order_message(order_id, order_details)
            # Send via Telegram bot (to be implemented)
            logger.info(f"Notification sent for order {order_id}")
    
    def notify_order_executed(self, order_id: int, execution_details: dict):
        """Notify about order execution.
        
        Args:
            order_id: Order ID
            execution_details: Execution details
        """
        if self.telegram_bot:
            logger.info(f"Execution notification sent for order {order_id}")
    
    def _format_order_message(self, order_id: int, order_details: dict) -> str:
        """Format order message for Telegram."""
        return f"""
🆕 New Order #{order_id}

Stock: {order_details.get('symbol', 'N/A')}
Type: {order_details.get('order_type', 'N/A')}
Quantity: {order_details.get('quantity', 'N/A')}
Entry: ₹{order_details.get('entry_price', 'N/A')}
Stop Loss: ₹{order_details.get('stop_loss', 'N/A')}
Target: ₹{order_details.get('target_price', 'N/A')}
Confidence: {order_details.get('confidence_score', 'N/A')}%

Please approve or reject this order.
        """.strip()
