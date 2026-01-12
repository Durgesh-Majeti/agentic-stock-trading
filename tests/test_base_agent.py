"""Unit tests for BaseAgent."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.base_agent import BaseAgent
from config.constants import AgentName
from database.repositories.analysis_repo import AnalysisRepository
from database.session import get_session


# Concrete implementation for testing
class TestAgent(BaseAgent):
    """Test agent implementation."""
    
    def __init__(self, name: str = "test_agent", model_role: str = "strategy"):
        super().__init__(name, model_role)
    
    def process(self, input_data: dict) -> dict:
        """Test process implementation."""
        return {"result": "success", "input": input_data}


class TestAgentNoLLM(BaseAgent):
    """Test agent without LLM."""
    
    def __init__(self, name: str = "test_agent_no_llm"):
        super().__init__(name, model_role=None)
    
    def process(self, input_data: dict) -> dict:
        """Test process implementation."""
        return {"result": "success"}


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    @pytest.fixture
    def mock_ollama_service(self):
        """Create mock OllamaService."""
        mock_service = Mock()
        mock_service.is_available = True
        mock_service.get_strategy_llm = Mock(return_value=Mock())
        mock_service.get_database_llm = Mock(return_value=Mock())
        mock_service.get_chatbot_llm = Mock(return_value=Mock())
        return mock_service
    
    @pytest.fixture
    def agent(self, mock_ollama_service):
        """Create test agent instance."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            return TestAgent("test_agent", "strategy")
    
    @pytest.fixture
    def agent_no_llm(self):
        """Create test agent without LLM."""
        return TestAgentNoLLM("test_agent_no_llm")
    
    def test_init_with_model_role(self, mock_ollama_service):
        """Test initialization with model role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("test_agent", "strategy")
            
            assert agent.name == "test_agent"
            assert agent.model_role == "strategy"
            assert agent.llm is not None
            mock_ollama_service.get_strategy_llm.assert_called_once()
    
    def test_init_without_model_role(self):
        """Test initialization without model role."""
        agent = TestAgentNoLLM("test_agent")
        
        assert agent.name == "test_agent"
        assert agent.model_role is None
        assert agent.llm is None
    
    def test_init_database_role(self, mock_ollama_service):
        """Test initialization with database role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("librarian", "database")
            
            assert agent.model_role == "database"
            mock_ollama_service.get_database_llm.assert_called_once()
    
    def test_init_chatbot_role(self, mock_ollama_service):
        """Test initialization with chatbot role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("telegram", "chatbot")
            
            assert agent.model_role == "chatbot"
            mock_ollama_service.get_chatbot_llm.assert_called_once()
    
    def test_process_abstract(self):
        """Test that process is abstract."""
        # Cannot instantiate BaseAgent directly
        with pytest.raises(TypeError):
            BaseAgent("test", "strategy")
    
    def test_process_implementation(self, agent):
        """Test process method implementation."""
        input_data = {"test": "data"}
        result = agent.process(input_data)
        
        assert result["result"] == "success"
        assert result["input"] == input_data
    
    @patch('agents.base_agent.get_session')
    def test_log_decision(self, mock_get_session, agent):
        """Test decision logging."""
        # Mock session context manager
        mock_session = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_session)
        mock_context.__exit__ = Mock(return_value=None)
        mock_get_session.return_value = mock_context
        
        mock_repo = Mock(spec=AnalysisRepository)
        with patch('agents.base_agent.AnalysisRepository', return_value=mock_repo):
            agent.log_decision(
                decision_type="TEST_DECISION",
                reasoning="Test reasoning",
                input_data={"input": "test"},
                output_data={"output": "test"},
                confidence_score=85.5
            )
            
            mock_repo.save_agent_decision.assert_called_once()
            call_args = mock_repo.save_agent_decision.call_args
            assert call_args.kwargs["decision_type"] == "TEST_DECISION"
            assert call_args.kwargs["reasoning"] == "Test reasoning"
            assert call_args.kwargs["confidence_score"] == 85.5
    
    def test_log_decision_error_handling(self, agent):
        """Test decision logging error handling."""
        # Should not raise error if logging fails
        with patch('agents.base_agent.get_session', side_effect=Exception("DB Error")):
            # Should not raise, just log error
            try:
                agent.log_decision(
                    decision_type="TEST",
                    reasoning="Test"
                )
            except Exception:
                pytest.fail("log_decision should not raise exception on error")
    
    def test_get_agent_name_enum(self, agent):
        """Test agent name to enum conversion."""
        # Test known mappings
        agent.name = "database_librarian"
        assert agent._get_agent_name_enum() == AgentName.DATABASE_LIBRARIAN
        
        agent.name = "strategy_specialist"
        assert agent._get_agent_name_enum() == AgentName.STRATEGY_SPECIALIST
        
        agent.name = "data_scraper"
        assert agent._get_agent_name_enum() == AgentName.DATA_SCRAPER
        
        agent.name = "telegram_assistant"
        assert agent._get_agent_name_enum() == AgentName.TELEGRAM_ASSISTANT
    
    def test_get_agent_name_enum_case_insensitive(self, agent):
        """Test case-insensitive agent name matching."""
        agent.name = "DATABASE_LIBRARIAN"
        assert agent._get_agent_name_enum() == AgentName.DATABASE_LIBRARIAN
    
    def test_get_agent_name_enum_unknown(self, agent):
        """Test unknown agent name handling."""
        agent.name = "unknown_agent"
        # Should default to STRATEGY_SPECIALIST
        result = agent._get_agent_name_enum()
        assert result == AgentName.STRATEGY_SPECIALIST
    
    def test_safe_process_success(self, agent):
        """Test safe_process with successful execution."""
        with patch.object(agent, 'log_decision'):
            result = agent.safe_process({"test": "data"})
            
            assert result["result"] == "success"
            agent.log_decision.assert_called_once()
    
    def test_safe_process_error(self, agent):
        """Test safe_process with error."""
        # Make process raise error
        def failing_process(input_data):
            raise ValueError("Test error")
        
        agent.process = failing_process
        
        with patch.object(agent, 'log_decision'):
            result = agent.safe_process({"test": "data"})
            
            assert result["error"] == "Test error"
            assert result["status"] == "failed"
            assert result["agent"] == "test_agent"
            # Should log error decision
            assert agent.log_decision.call_count == 1
    
    def test_safe_process_no_log(self, agent):
        """Test safe_process without logging."""
        with patch.object(agent, 'log_decision') as mock_log:
            result = agent.safe_process({"test": "data"}, log_decision=False)
            
            assert result["result"] == "success"
            mock_log.assert_not_called()
    
    def test_validate_input(self, agent):
        """Test input validation."""
        # Valid input
        assert agent.validate_input(
            {"required1": "value1", "required2": "value2"},
            required_fields=["required1", "required2"]
        ) is True
        
        # Missing required field
        assert agent.validate_input(
            {"required1": "value1"},
            required_fields=["required1", "required2"]
        ) is False
        
        # With optional fields
        assert agent.validate_input(
            {"required1": "value1", "optional1": "value2"},
            required_fields=["required1"],
            optional_fields=["optional1"]
        ) is True
    
    def test_validate_output(self, agent):
        """Test output validation."""
        # Valid output
        assert agent.validate_output(
            {"field1": "value1", "field2": "value2"},
            required_fields=["field1", "field2"]
        ) is True
        
        # Missing required field
        assert agent.validate_output(
            {"field1": "value1"},
            required_fields=["field1", "field2"]
        ) is False
    
    def test_get_llm(self, agent):
        """Test getting LLM instance."""
        assert agent.get_llm() is not None
    
    def test_get_llm_no_llm(self, agent_no_llm):
        """Test getting LLM when not available."""
        assert agent_no_llm.get_llm() is None
    
    def test_is_llm_available(self, mock_ollama_service):
        """Test LLM availability check."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("test_agent", "strategy")
            
            assert agent.is_llm_available() is True
    
    def test_is_llm_available_false(self, agent_no_llm):
        """Test LLM availability when not initialized."""
        assert agent_no_llm.is_llm_available() is False
    
    def test_news_sentiment_role(self, mock_ollama_service):
        """Test initialization with news_sentiment role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("sentiment_analyst", "news_sentiment")
            
            assert agent.model_role == "news_sentiment"
            # Should use strategy LLM
            mock_ollama_service.get_strategy_llm.assert_called_once()
    
    def test_guardian_role(self, mock_ollama_service):
        """Test initialization with guardian role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("guardian", "guardian")
            
            assert agent.model_role == "guardian"
            # Should use strategy LLM
            mock_ollama_service.get_strategy_llm.assert_called_once()
    
    def test_unknown_model_role(self, mock_ollama_service):
        """Test initialization with unknown model role."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            agent = TestAgent("test_agent", "unknown_role")
            
            assert agent.llm is None
