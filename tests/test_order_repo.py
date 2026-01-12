"""Unit tests for OrderRepository."""
import pytest
from datetime import datetime
from database.repositories.order_repo import OrderRepository
from database.models import Order, Stock
from config.constants import OrderStatus, OrderType, Exchange


class TestOrderRepository:
    """Test cases for OrderRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create OrderRepository instance."""
        return OrderRepository(temp_db)
    
    @pytest.fixture
    def sample_stock(self, temp_db):
        """Create sample stock."""
        stock = Stock(
            symbol="TEST-EQ",
            name="Test Stock",
            exchange=Exchange.NSE,
            sector="IT"
        )
        temp_db.add(stock)
        temp_db.commit()
        temp_db.refresh(stock)
        return stock
    
    def test_create_order(self, repo, sample_stock):
        """Test creating a new order."""
        order = repo.create_order(
            stock_id=sample_stock.id,
            order_type=OrderType.BUY,
            quantity=10,
            entry_price=100.0,
            stop_loss=98.0,
            target_price=104.0,
            confidence_score=0.85
        )
        
        assert order.id is not None
        assert order.order_status == OrderStatus.PENDING_APPROVAL
        assert order.quantity == 10
        assert order.entry_price == 100.0
    
    def test_get_pending_orders(self, repo, sample_stock):
        """Test getting pending orders."""
        # Create pending order
        repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        
        # Create and approve another order
        order2 = repo.create_order(
            sample_stock.id, OrderType.BUY, 5, 50.0, 49.0, 52.0, 0.75
        )
        repo.approve_order(order2.id)
        
        pending = repo.get_pending_orders()
        assert len(pending) == 1
        assert pending[0].order_status == OrderStatus.PENDING_APPROVAL
    
    def test_get_order(self, repo, sample_stock):
        """Test getting order by ID."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        
        found = repo.get_order(order.id)
        assert found is not None
        assert found.id == order.id
    
    def test_approve_order(self, repo, sample_stock):
        """Test approving an order."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        
        approved = repo.approve_order(order.id)
        assert approved is not None
        assert approved.order_status == OrderStatus.APPROVED
        assert approved.approved_at is not None
    
    def test_reject_order(self, repo, sample_stock):
        """Test rejecting an order."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        
        rejected = repo.reject_order(order.id)
        assert rejected is not None
        assert rejected.order_status == OrderStatus.REJECTED
        assert rejected.rejected_at is not None
    
    def test_mark_executed(self, repo, sample_stock):
        """Test marking order as executed."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        repo.approve_order(order.id)
        
        executed = repo.mark_executed(order.id, 100.5, "Order executed successfully")
        assert executed is not None
        assert executed.order_status == OrderStatus.EXECUTED
        assert executed.executed_price == 100.5
        assert executed.execution_message == "Order executed successfully"
        assert executed.executed_at is not None
    
    def test_mark_failed(self, repo, sample_stock):
        """Test marking order as failed."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        repo.approve_order(order.id)
        
        failed = repo.mark_failed(order.id, "Connection timeout")
        assert failed is not None
        assert failed.order_status == OrderStatus.FAILED
        assert failed.execution_message == "Connection timeout"
    
    def test_get_recent_orders(self, repo, sample_stock):
        """Test getting recent orders."""
        # Create multiple orders
        repo.create_order(sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85)
        repo.create_order(sample_stock.id, OrderType.SELL, 5, 50.0, 49.0, 52.0, 0.75)
        
        recent = repo.get_recent_orders(limit=10)
        assert len(recent) >= 2
    
    def test_approve_already_executed_order(self, repo, sample_stock):
        """Test that approving an executed order doesn't change status."""
        order = repo.create_order(
            sample_stock.id, OrderType.BUY, 10, 100.0, 98.0, 104.0, 0.85
        )
        repo.approve_order(order.id)
        repo.mark_executed(order.id, 100.5)
        
        # Try to approve again (should not change)
        approved = repo.approve_order(order.id)
        assert approved.order_status == OrderStatus.EXECUTED
