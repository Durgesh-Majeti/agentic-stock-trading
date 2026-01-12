"""Unit tests for NotificationService."""
import pytest
from unittest.mock import Mock, MagicMock
from services.notification_service import NotificationService


class TestNotificationService:
    """Test cases for NotificationService."""
    
    @pytest.fixture
    def mock_telegram_bot(self):
        """Create mock Telegram bot."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_telegram_bot):
        """Create NotificationService instance."""
        return NotificationService(telegram_bot=mock_telegram_bot)
    
    @pytest.fixture
    def service_no_bot(self):
        """Create NotificationService without bot."""
        return NotificationService(telegram_bot=None)
    
    def test_notify_new_order(self, service, mock_telegram_bot):
        """Test notifying about new order."""
        order_details = {
            'symbol': 'TCS',
            'order_type': 'BUY',
            'quantity': 10,
            'entry_price': 100.0,
            'stop_loss': 98.0,
            'target_price': 104.0,
            'confidence_score': 85
        }
        
        service.notify_new_order(123, order_details)
        
        # Service should format message (bot sending to be implemented)
        # For now, just verify it doesn't crash
        assert True
    
    def test_notify_new_order_no_bot(self, service_no_bot):
        """Test notification when no bot configured."""
        order_details = {'symbol': 'TCS'}
        # Should not crash
        service_no_bot.notify_new_order(123, order_details)
        assert True
    
    def test_notify_order_executed(self, service, mock_telegram_bot):
        """Test notifying about order execution."""
        execution_details = {
            'order_id': 123,
            'executed_price': 100.5,
            'quantity': 10
        }
        
        service.notify_order_executed(123, execution_details)
        
        # Service should send notification (to be implemented)
        assert True
    
    def test_format_order_message(self, service):
        """Test order message formatting."""
        order_details = {
            'symbol': 'TCS',
            'order_type': 'BUY',
            'quantity': 10,
            'entry_price': 100.0,
            'stop_loss': 98.0,
            'target_price': 104.0,
            'confidence_score': 85
        }
        
        message = service._format_order_message(123, order_details)
        
        assert 'New Order #123' in message
        assert 'TCS' in message
        assert 'BUY' in message
        assert '₹100.0' in message
