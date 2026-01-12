"""Unit tests for TradingOrchestrator."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from orchestrator.orchestrator import TradingOrchestrator
from orchestrator.exceptions import (
    WorkflowNotFoundError,
    AgentNotFoundError,
    ContractValidationError
)


class TestTradingOrchestrator:
    """Test cases for TradingOrchestrator."""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents."""
        return {
            "librarian": Mock(),
            "scraper": Mock(),
            "strategy": Mock()
        }
    
    @pytest.fixture
    def orchestrator(self, mock_agents):
        """Create orchestrator instance."""
        return TradingOrchestrator(agents=mock_agents)
    
    def test_init_with_agents(self, mock_agents):
        """Test initialization with agents."""
        orchestrator = TradingOrchestrator(agents=mock_agents)
        assert orchestrator.agents == mock_agents
        assert len(orchestrator.circuit_breakers) == len(mock_agents)
    
    def test_init_without_agents(self):
        """Test initialization without agents."""
        orchestrator = TradingOrchestrator()
        assert orchestrator.agents == {}
    
    @pytest.mark.asyncio
    async def test_call_agent_success(self, orchestrator, mock_agents):
        """Test successful agent call."""
        # Agent.process() is synchronous, so use Mock not AsyncMock
        expected_result = {
            "sql": "SELECT * FROM stocks",
            "results": [],
            "count": 0
        }
        mock_agents["librarian"].process = Mock(return_value=expected_result)
        
        # Mock the cache manager to directly call the function
        async def mock_get_or_call(agent_name, input_data, call_func):
            # call_func is async, await it
            return await call_func(input_data)
        
        orchestrator.cache_manager.get_or_call = mock_get_or_call
        
        result = await orchestrator._call_agent(
            "librarian",
            {"query": "test"},
            use_cache=True
        )
        
        assert result["sql"] == "SELECT * FROM stocks"
        mock_agents["librarian"].process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_agent_not_found(self, orchestrator):
        """Test calling non-existent agent."""
        with pytest.raises(AgentNotFoundError):
            await orchestrator._call_agent("nonexistent", {})
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, orchestrator):
        """Test executing non-existent workflow."""
        with pytest.raises(WorkflowNotFoundError):
            await orchestrator.execute_workflow("nonexistent", {})
    
    def test_format_agent_input(self, orchestrator):
        """Test input formatting."""
        raw_data = {"query": "test", "max_results": 10}
        formatted = orchestrator._format_agent_input("librarian", raw_data)
        assert formatted == raw_data  # Simplified for now
    
    def test_validate_agent_output(self, orchestrator):
        """Test output validation."""
        output = {"sql": "SELECT *", "results": []}
        assert orchestrator._validate_agent_output("librarian", output) is True
