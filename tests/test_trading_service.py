"""Unit tests for TradingService."""
import pytest
from unittest.mock import Mock, MagicMock
from database.repositories.order_repo import OrderRepository
from database.repositories.trade_repo import TradeRepository
from database.repositories.portfolio_repo import PortfolioRepository
from services.trading_service import TradingService
from config.constants import OrderStatus, OrderType


class TestTradingService:
    """Test cases for TradingService."""
    
    @pytest.fixture
    def mock_order_repo(self):
        """Create mock order repository."""
        return Mock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_trade_repo(self):
        """Create mock trade repository."""
        return Mock(spec=TradeRepository)
    
    @pytest.fixture
    def mock_portfolio_repo(self):
        """Create mock portfolio repository."""
        return Mock(spec=PortfolioRepository)
    
    @pytest.fixture
    def service(self, mock_order_repo, mock_trade_repo, mock_portfolio_repo):
        """Create TradingService instance."""
        return TradingService(mock_order_repo, mock_trade_repo, mock_portfolio_repo)
    
    def test_create_trade_from_order_success(self, service, mock_order_repo, mock_trade_repo):
        """Test creating trade from approved order."""
        # Mock approved order
        mock_order = Mock()
        mock_order.order_status = OrderStatus.APPROVED
        mock_order.stock_id = 1
        mock_order.order_id = 123
        mock_order.order_type = OrderType.BUY
        mock_order.quantity = 10
        mock_order.entry_price = 100.0
        mock_order.executed_price = None
        mock_order.stop_loss = 98.0
        mock_order.target_price = 104.0
        
        mock_order_repo.get_order.return_value = mock_order
        
        # Mock trade creation
        mock_trade = Mock()
        mock_trade.id = 456
        mock_trade_repo.create_trade.return_value = mock_trade
        
        trade_id = service.create_trade_from_order(123)
        
        assert trade_id == 456
        mock_trade_repo.create_trade.assert_called_once()
    
    def test_create_trade_from_order_not_approved(self, service, mock_order_repo):
        """Test creating trade from non-approved order."""
        mock_order = Mock()
        mock_order.order_status = OrderStatus.PENDING_APPROVAL
        mock_order_repo.get_order.return_value = mock_order
        
        trade_id = service.create_trade_from_order(123)
        
        assert trade_id is None
    
    def test_create_trade_from_order_not_found(self, service, mock_order_repo):
        """Test creating trade from non-existent order."""
        mock_order_repo.get_order.return_value = None
        
        trade_id = service.create_trade_from_order(999)
        
        assert trade_id is None
    
    def test_create_trade_from_order_with_executed_price(self, service, mock_order_repo, mock_trade_repo):
        """Test creating trade using executed_price when entry_price is None."""
        mock_order = Mock()
        mock_order.order_status = OrderStatus.APPROVED
        mock_order.stock_id = 1
        mock_order.order_id = 123
        mock_order.order_type = OrderType.BUY
        mock_order.quantity = 10
        mock_order.entry_price = None
        mock_order.executed_price = 100.5
        mock_order.stop_loss = 98.0
        mock_order.target_price = 104.0
        
        mock_order_repo.get_order.return_value = mock_order
        mock_trade = Mock()
        mock_trade.id = 456
        mock_trade_repo.create_trade.return_value = mock_trade
        
        trade_id = service.create_trade_from_order(123)
        
        assert trade_id == 456
        # Verify executed_price was used
        call_args = mock_trade_repo.create_trade.call_args
        assert call_args[1]['entry_price'] == 100.5
