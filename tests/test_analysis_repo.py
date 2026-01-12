"""Unit tests for AnalysisRepository."""
import pytest
from database.repositories.analysis_repo import AnalysisRepository
from database.models import Stock, AgentDecision, ScreeningSignal
from config.constants import AgentName, SignalType, Exchange


class TestAnalysisRepository:
    """Test cases for AnalysisRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create AnalysisRepository instance."""
        return AnalysisRepository(temp_db)
    
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
    
    def test_save_agent_decision(self, repo, sample_stock):
        """Test saving agent decision."""
        decision = repo.save_agent_decision(
            agent_name=AgentName.STRATEGY_SPECIALIST,
            decision_type="BUY_SIGNAL",
            reasoning="Strong RSI and MACD signals",
            confidence_score=0.85,
            stock_id=sample_stock.id,
            input_data='{"rsi": 28.5, "macd": 2.3}',
            output_data='{"action": "BUY", "price": 100.0}'
        )
        
        assert decision.id is not None
        assert decision.agent_name == AgentName.STRATEGY_SPECIALIST
        assert decision.confidence_score == 0.85
        assert decision.stock_id == sample_stock.id
    
    def test_get_recent_decisions(self, repo, sample_stock):
        """Test getting recent decisions."""
        repo.save_agent_decision(
            AgentName.STRATEGY_SPECIALIST, "BUY_SIGNAL", "Reasoning", 0.85, sample_stock.id
        )
        repo.save_agent_decision(
            AgentName.DATABASE_LIBRARIAN, "QUERY", "SQL query", 0.90
        )
        
        decisions = repo.get_recent_decisions(limit=10)
        assert len(decisions) >= 2
    
    def test_get_recent_decisions_filtered(self, repo, sample_stock):
        """Test getting recent decisions filtered by agent."""
        repo.save_agent_decision(
            AgentName.STRATEGY_SPECIALIST, "BUY_SIGNAL", "Reasoning", 0.85, sample_stock.id
        )
        repo.save_agent_decision(
            AgentName.DATABASE_LIBRARIAN, "QUERY", "SQL query", 0.90
        )
        
        decisions = repo.get_recent_decisions(agent_name=AgentName.STRATEGY_SPECIALIST)
        assert len(decisions) >= 1
        assert all(d.agent_name == AgentName.STRATEGY_SPECIALIST for d in decisions)
    
    def test_create_screening_signal(self, repo, sample_stock):
        """Test creating screening signal."""
        signal = repo.create_screening_signal(
            stock_id=sample_stock.id,
            signal_type=SignalType.BUY,
            confidence_score=0.82,
            entry_price=100.0,
            stop_loss=98.0,
            target_price=104.0
        )
        
        assert signal.id is not None
        assert signal.signal_type == SignalType.BUY
        assert signal.confidence_score == 0.82
        assert signal.entry_price == 100.0
    
    def test_get_recent_signals(self, repo, sample_stock):
        """Test getting recent signals."""
        repo.create_screening_signal(
            sample_stock.id, SignalType.BUY, 0.85, 100.0, 98.0, 104.0
        )
        repo.create_screening_signal(
            sample_stock.id, SignalType.SELL, 0.70, 50.0, 51.0, 48.0
        )
        
        signals = repo.get_recent_signals(limit=10)
        assert len(signals) >= 2
    
    def test_get_recent_signals_filtered(self, repo, sample_stock):
        """Test getting recent signals filtered by type."""
        repo.create_screening_signal(
            sample_stock.id, SignalType.BUY, 0.85, 100.0, 98.0, 104.0
        )
        repo.create_screening_signal(
            sample_stock.id, SignalType.SELL, 0.70, 50.0, 51.0, 48.0
        )
        
        buy_signals = repo.get_recent_signals(signal_type=SignalType.BUY)
        assert len(buy_signals) >= 1
        assert all(s.signal_type == SignalType.BUY for s in buy_signals)
    
    def test_get_recent_signals_min_confidence(self, repo, sample_stock):
        """Test getting signals with minimum confidence."""
        repo.create_screening_signal(
            sample_stock.id, SignalType.BUY, 0.85, 100.0, 98.0, 104.0
        )
        repo.create_screening_signal(
            sample_stock.id, SignalType.BUY, 0.60, 50.0, 49.0, 52.0
        )
        
        high_confidence = repo.get_recent_signals(min_confidence=0.75)
        assert len(high_confidence) >= 1
        assert all(s.confidence_score >= 0.75 for s in high_confidence)
