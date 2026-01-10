"""Unit tests for AnalysisService."""
import pytest
from unittest.mock import Mock, MagicMock
from database.repositories.analysis_repo import AnalysisRepository
from database.repositories.market_data_repo import MarketDataRepository
from services.analysis_service import AnalysisService
from config.constants import SignalType, AgentName
from datetime import date


class TestAnalysisService:
    """Test cases for AnalysisService."""
    
    @pytest.fixture
    def mock_analysis_repo(self):
        """Create mock analysis repository."""
        return Mock(spec=AnalysisRepository)
    
    @pytest.fixture
    def mock_market_data_repo(self):
        """Create mock market data repository."""
        return Mock(spec=MarketDataRepository)
    
    @pytest.fixture
    def service(self, mock_analysis_repo, mock_market_data_repo):
        """Create AnalysisService instance."""
        return AnalysisService(mock_analysis_repo, mock_market_data_repo)
    
    def test_get_stock_analysis(self, service, mock_analysis_repo, mock_market_data_repo):
        """Test getting stock analysis."""
        # Mock signals (method doesn't filter by stock_id, returns all)
        mock_signal = Mock()
        mock_signal.id = 1
        mock_signal.signal_type = SignalType.BUY
        mock_signal.confidence_score = 0.85
        mock_signal.entry_price = 100.0
        mock_signal.stop_loss = 98.0
        mock_signal.target_price = 104.0
        mock_signal.created_at = date.today()
        mock_analysis_repo.get_recent_signals.return_value = [mock_signal]
        
        # Mock decisions (method doesn't filter by stock_id, returns all)
        mock_decision = Mock()
        mock_decision.id = 1
        mock_decision.agent_name = AgentName.STRATEGY_SPECIALIST
        mock_decision.decision_type = "BUY_SIGNAL"
        mock_decision.confidence_score = 0.85
        mock_decision.created_at = date.today()
        mock_analysis_repo.get_recent_decisions.return_value = [mock_decision]
        
        # Mock market data
        mock_market_data = Mock()
        mock_market_data.date = date.today()
        mock_market_data.close = 100.0
        mock_market_data.rsi = 28.5
        mock_market_data.macd = 2.3
        mock_market_data.bollinger_upper = 105.0
        mock_market_data.bollinger_lower = 95.0
        mock_market_data_repo.get_latest_daily_data.return_value = mock_market_data
        
        analysis = service.get_stock_analysis(1)
        
        assert 'signals' in analysis
        assert 'decisions' in analysis
        assert 'market_data' in analysis
        assert len(analysis['signals']) == 1
        assert analysis['signals'][0]['signal_type'] == SignalType.BUY.value
    
    def test_get_stock_analysis_no_market_data(self, service, mock_analysis_repo, mock_market_data_repo):
        """Test getting stock analysis when no market data."""
        mock_analysis_repo.get_recent_signals.return_value = []
        mock_analysis_repo.get_recent_decisions.return_value = []
        mock_market_data_repo.get_latest_daily_data.return_value = None
        
        analysis = service.get_stock_analysis(1)
        
        assert analysis['market_data'] is None
        assert analysis['signals'] == []
        assert analysis['decisions'] == []
