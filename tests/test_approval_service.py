"""Unit tests for ApprovalService."""
import pytest
from unittest.mock import Mock, MagicMock
from database.repositories.order_repo import OrderRepository
from database.repositories.user_action_repo import UserActionRepository
from services.approval_service import ApprovalService
from config.constants import OrderStatus


class TestApprovalService:
    """Test cases for ApprovalService."""
    
    @pytest.fixture
    def mock_order_repo(self):
        """Create mock order repository."""
        return Mock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_user_action_repo(self):
        """Create mock user action repository."""
        return Mock(spec=UserActionRepository)
    
    @pytest.fixture
    def service(self, mock_order_repo, mock_user_action_repo):
        """Create ApprovalService instance."""
        return ApprovalService(mock_order_repo, mock_user_action_repo)
    
    def test_get_pending_approvals(self, service, mock_order_repo):
        """Test getting pending approvals."""
        mock_orders = [Mock(), Mock()]
        mock_order_repo.get_pending_orders.return_value = mock_orders
        
        result = service.get_pending_approvals()
        
        assert result == mock_orders
        mock_order_repo.get_pending_orders.assert_called_once()
    
    def test_approve_order_success(self, service, mock_order_repo, mock_user_action_repo):
        """Test approving an order successfully."""
        mock_order = Mock()
        mock_order.id = 123
        mock_order.stock_id = 1
        mock_order_repo.approve_order.return_value = mock_order
        
        result = service.approve_order(123, user_id="user_123")
        
        assert result is True
        mock_order_repo.approve_order.assert_called_once_with(123)
        mock_user_action_repo.log_action.assert_called_once()
        call_args = mock_user_action_repo.log_action.call_args
        assert call_args[1]['action_type'] == "APPROVE_ORDER"
        assert call_args[1]['user_id'] == "user_123"
    
    def test_approve_order_failure(self, service, mock_order_repo):
        """Test approving non-existent order."""
        mock_order_repo.approve_order.return_value = None
        
        result = service.approve_order(999)
        
        assert result is False
    
    def test_reject_order_success(self, service, mock_order_repo, mock_user_action_repo):
        """Test rejecting an order successfully."""
        mock_order = Mock()
        mock_order.id = 123
        mock_order.stock_id = 1
        mock_order_repo.reject_order.return_value = mock_order
        
        result = service.reject_order(123, user_id="user_123")
        
        assert result is True
        mock_order_repo.reject_order.assert_called_once_with(123)
        mock_user_action_repo.log_action.assert_called_once()
        call_args = mock_user_action_repo.log_action.call_args
        assert call_args[1]['action_type'] == "REJECT_ORDER"
    
    def test_reject_order_failure(self, service, mock_order_repo):
        """Test rejecting non-existent order."""
        mock_order_repo.reject_order.return_value = None
        
        result = service.reject_order(999)
        
        assert result is False
