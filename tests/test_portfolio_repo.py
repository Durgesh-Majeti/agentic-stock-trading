"""Unit tests for PortfolioRepository."""
import pytest
from database.repositories.portfolio_repo import PortfolioRepository
from database.models import Portfolio, Stock
from config.constants import Exchange


class TestPortfolioRepository:
    """Test cases for PortfolioRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create PortfolioRepository instance."""
        return PortfolioRepository(temp_db)
    
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
    
    def test_get_portfolio_empty(self, repo):
        """Test getting empty portfolio."""
        portfolio = repo.get_portfolio()
        assert portfolio == []
    
    def test_add_holding_new(self, repo, sample_stock):
        """Test adding new holding."""
        holding = repo.add_or_update_holding(
            stock_id=sample_stock.id,
            quantity=10,
            price=100.0,
            current_price=100.0
        )
        
        assert holding.id is not None
        assert holding.quantity == 10
        assert holding.avg_price == 100.0
        assert holding.current_price == 100.0
        assert holding.unrealized_pnl == 0.0
    
    def test_add_holding_update(self, repo, sample_stock):
        """Test updating existing holding."""
        # Add initial holding
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        # Add more shares at different price
        holding = repo.add_or_update_holding(sample_stock.id, 5, 110.0, 110.0)
        
        assert holding.quantity == 15
        # Average price: (10*100 + 5*110) / 15 = 103.33
        assert abs(holding.avg_price - 103.33) < 0.01
        assert holding.unrealized_pnl == (110.0 - holding.avg_price) * 15
    
    def test_get_holding(self, repo, sample_stock):
        """Test getting holding for a stock."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        holding = repo.get_holding(sample_stock.id)
        assert holding is not None
        assert holding.stock_id == sample_stock.id
        assert holding.quantity == 10
    
    def test_reduce_holding_partial(self, repo, sample_stock):
        """Test reducing holding partially."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        holding, realized_pnl = repo.reduce_holding(sample_stock.id, 5, 110.0)
        
        assert holding is not None
        assert holding.quantity == 5
        assert realized_pnl == 50.0  # (110 - 100) * 5
    
    def test_reduce_holding_complete(self, repo, sample_stock):
        """Test reducing holding completely."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        holding, realized_pnl = repo.reduce_holding(sample_stock.id, 10, 110.0)
        
        assert holding is None  # Should be deleted
        assert realized_pnl == 100.0  # (110 - 100) * 10
    
    def test_reduce_holding_insufficient(self, repo, sample_stock):
        """Test reducing more than available."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        holding, realized_pnl = repo.reduce_holding(sample_stock.id, 15, 110.0)
        
        assert holding is None
        assert realized_pnl == 0.0
    
    def test_update_current_prices(self, repo, sample_stock):
        """Test updating current prices."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 100.0)
        
        repo.update_current_prices(sample_stock.id, 110.0)
        
        holding = repo.get_holding(sample_stock.id)
        assert holding.current_price == 110.0
        assert holding.unrealized_pnl == 100.0  # (110 - 100) * 10
    
    def test_get_total_portfolio_value(self, repo, sample_stock):
        """Test getting total portfolio value."""
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 110.0)
        
        # Create another stock and holding
        stock2 = Stock(symbol="TEST2-EQ", name="Test Stock 2", exchange=Exchange.NSE)
        repo.session.add(stock2)
        repo.session.commit()
        repo.session.refresh(stock2)
        
        repo.add_or_update_holding(stock2.id, 5, 50.0, 60.0)
        
        total_value = repo.get_total_portfolio_value()
        assert total_value == (110.0 * 10) + (60.0 * 5)  # 1100 + 300 = 1400
    
    def test_get_total_pnl(self, repo, sample_stock):
        """Test getting total P&L."""
        # Add holding with unrealized P&L
        repo.add_or_update_holding(sample_stock.id, 10, 100.0, 110.0)
        
        # Reduce some shares (realized P&L)
        repo.reduce_holding(sample_stock.id, 5, 115.0)
        
        realized, unrealized = repo.get_total_pnl()
        assert realized == 75.0  # (115 - 100) * 5
        assert unrealized > 0  # Remaining shares at profit
