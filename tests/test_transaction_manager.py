"""Unit tests for TransactionManager."""
import pytest
import asyncio
from orchestrator.transaction_manager import TransactionManager, WorkflowTransaction


class TestWorkflowTransaction:
    """Test cases for WorkflowTransaction."""
    
    @pytest.fixture
    def transaction(self):
        """Create transaction instance."""
        return WorkflowTransaction("test-workflow-123")
    
    def test_add_step(self, transaction):
        """Test adding step to transaction."""
        transaction.add_step("step1", {"result": "test"})
        
        assert len(transaction.executed_steps) == 1
        assert transaction.executed_steps[0]["step"] == "step1"
    
    @pytest.mark.asyncio
    async def test_rollback(self, transaction):
        """Test transaction rollback."""
        rollback_called = []
        
        def rollback_func():
            rollback_called.append("rolled_back")
        
        transaction.add_step("step1", {}, rollback_func)
        await transaction.rollback()
        
        assert len(rollback_called) == 1
    
    @pytest.mark.asyncio
    async def test_rollback_async(self, transaction):
        """Test async rollback function."""
        rollback_called = []
        
        async def async_rollback():
            rollback_called.append("rolled_back")
        
        transaction.add_step("step1", {}, async_rollback)
        await transaction.rollback()
        
        assert len(rollback_called) == 1


class TestTransactionManager:
    """Test cases for TransactionManager."""
    
    @pytest.fixture
    def transaction_manager(self):
        """Create transaction manager instance."""
        return TransactionManager()
    
    def test_begin_transaction(self, transaction_manager):
        """Test beginning transaction."""
        transaction = transaction_manager.begin_transaction("test-id")
        
        assert transaction.workflow_id == "test-id"
        assert transaction_manager.get_transaction("test-id") == transaction
    
    def test_get_transaction(self, transaction_manager):
        """Test getting transaction."""
        transaction = transaction_manager.begin_transaction("test-id")
        
        retrieved = transaction_manager.get_transaction("test-id")
        assert retrieved == transaction
    
    @pytest.mark.asyncio
    async def test_commit(self, transaction_manager):
        """Test committing transaction."""
        transaction = transaction_manager.begin_transaction("test-id")
        transaction.add_step("step1", {})
        
        await transaction_manager.commit("test-id")
        
        assert transaction_manager.get_transaction("test-id") is None
    
    @pytest.mark.asyncio
    async def test_rollback(self, transaction_manager):
        """Test rolling back transaction."""
        transaction = transaction_manager.begin_transaction("test-id")
        transaction.add_step("step1", {})
        
        await transaction_manager.rollback("test-id")
        
        assert transaction_manager.get_transaction("test-id") is None
