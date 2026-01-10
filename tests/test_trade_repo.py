"""Unit tests for TradeRepository."""
import pytest
from datetime import datetime
from database.repositories.trade_repo import TradeRepository
from database.models import Trade, Stock
from config.constants import OrderType, TradeStatus, Exchange


class TestTradeRepository:
    """Test cases for TradeRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create TradeRepository instance."""
        return TradeRepository(temp_db)
    
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
    
    def test_create_trade(self, repo, sample_stock):
        """Test creating a new trade."""
        trade = repo.create_trade(
            stock_id=sample_stock.id,
            order_id=None,
            buy_sell=OrderType.BUY,
            quantity=10,
            entry_price=100.0,
            stop_loss=98.0,
            target=104.0
        )
        
        assert trade.id is not None
        assert trade.status == TradeStatus.OPEN
        assert trade.quantity == 10
        assert trade.entry_price == 100.0
        assert trade.executed_at is not None
    
    def test_get_open_trades(self, repo, sample_stock):
        """Test getting open trades."""
        # Create open trade
        trade1 = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        
        # Create and close another trade
        trade2 = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 5, 50.0, 49.0, 52.0
        )
        repo.close_trade(trade2.id, 52.0)
        
        open_trades = repo.get_open_trades()
        assert len(open_trades) == 1
        assert open_trades[0].id == trade1.id
    
    def test_get_trade(self, repo, sample_stock):
        """Test getting trade by ID."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        
        found = repo.get_trade(trade.id)
        assert found is not None
        assert found.id == trade.id
    
    def test_close_trade_buy(self, repo, sample_stock):
        """Test closing a BUY trade."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        
        closed = repo.close_trade(trade.id, 104.0)
        assert closed is not None
        assert closed.status == TradeStatus.CLOSED
        assert closed.exit_price == 104.0
        assert closed.pnl == 40.0  # (104 - 100) * 10
        assert closed.pnl_percent == 4.0  # (40 / 1000) * 100
        assert closed.closed_at is not None
    
    def test_close_trade_sell(self, repo, sample_stock):
        """Test closing a SELL trade."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.SELL, 10, 100.0, 102.0, 96.0
        )
        
        closed = repo.close_trade(trade.id, 96.0)
        assert closed is not None
        assert closed.pnl == 40.0  # (100 - 96) * 10
        assert closed.pnl_percent == 4.0
    
    def test_close_trade_loss(self, repo, sample_stock):
        """Test closing trade at a loss."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        
        closed = repo.close_trade(trade.id, 98.0)
        assert closed.pnl == -20.0  # (98 - 100) * 10
        assert closed.pnl_percent == -2.0
    
    def test_close_trade_stop_loss(self, repo, sample_stock):
        """Test closing trade with stop loss status."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        
        closed = repo.close_trade(trade.id, 98.0, TradeStatus.STOP_LOSS_HIT)
        assert closed.status == TradeStatus.STOP_LOSS_HIT
    
    def test_get_recent_trades(self, repo, sample_stock):
        """Test getting recent trades."""
        repo.create_trade(sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0)
        repo.create_trade(sample_stock.id, None, OrderType.SELL, 5, 50.0, 49.0, 52.0)
        
        recent = repo.get_recent_trades(limit=10)
        assert len(recent) >= 2
    
    def test_get_trades_by_stock(self, repo, sample_stock):
        """Test getting trades for a specific stock."""
        # Create trades for this stock
        trade1 = repo.create_trade(sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0)
        trade2 = repo.create_trade(sample_stock.id, None, OrderType.BUY, 5, 50.0, 49.0, 52.0)
        
        trades = repo.get_trades_by_stock(sample_stock.id)
        assert len(trades) >= 2
        assert all(t.stock_id == sample_stock.id for t in trades)
    
    def test_close_already_closed_trade(self, repo, sample_stock):
        """Test that closing an already closed trade doesn't change it."""
        trade = repo.create_trade(
            sample_stock.id, None, OrderType.BUY, 10, 100.0, 98.0, 104.0
        )
        repo.close_trade(trade.id, 104.0)
        
        # Try to close again (should not change)
        closed = repo.close_trade(trade.id, 105.0)
        assert closed.exit_price == 104.0  # Original exit price
