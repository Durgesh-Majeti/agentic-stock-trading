"""Unit tests for WorkflowExecutor."""
import pytest
import asyncio
from unittest.mock import AsyncMock
from orchestrator.workflow_executor import WorkflowExecutor


class TestWorkflowExecutor:
    """Test cases for WorkflowExecutor."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return WorkflowExecutor()
    
    @pytest.fixture
    def mock_call_func(self):
        """Create mock call function."""
        async def call_func(input_data):
            return {"result": input_data["value"] * 2}
        return call_func
    
    @pytest.mark.asyncio
    async def test_execute_parallel(self, executor, mock_call_func):
        """Test parallel execution."""
        inputs = [{"value": i} for i in range(5)]
        
        results = await executor.execute_parallel(
            "test_agent",
            inputs,
            mock_call_func,
            max_concurrent=5,
            rate_limit=10
        )
        
        assert len(results) == 5
        assert results[0]["result"] == 0
        assert results[4]["result"] == 8
    
    @pytest.mark.asyncio
    async def test_execute_parallel_with_errors(self, executor):
        """Test parallel execution with errors."""
        async def failing_func(input_data):
            if input_data["value"] == 2:
                raise ValueError("Test error")
            return {"result": input_data["value"]}
        
        inputs = [{"value": i} for i in range(5)]
        
        results = await executor.execute_parallel(
            "test_agent",
            inputs,
            failing_func,
            max_concurrent=5
        )
        
        assert len(results) == 5
        assert "error" in results[2]
        assert results[0]["result"] == 0
    
    @pytest.mark.asyncio
    async def test_execute_sequential(self, executor, mock_call_func):
        """Test sequential execution."""
        inputs = [{"value": i} for i in range(3)]
        
        results = await executor.execute_sequential(
            "test_agent",
            inputs,
            mock_call_func,
            rate_limit=10
        )
        
        assert len(results) == 3
        assert results[0]["result"] == 0
        assert results[2]["result"] == 4
