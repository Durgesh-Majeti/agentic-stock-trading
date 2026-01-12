"""Unit tests for WorkflowState and WorkflowStateManager."""
import pytest
from datetime import datetime
from orchestrator.workflow_state import WorkflowState, WorkflowStateManager
from orchestrator.exceptions import WorkflowStateError


class TestWorkflowState:
    """Test cases for WorkflowState."""
    
    @pytest.fixture
    def workflow_state(self):
        """Create workflow state instance."""
        return WorkflowState("test-workflow-123")
    
    def test_save_checkpoint(self, workflow_state):
        """Test saving checkpoint."""
        data = {"result": "test"}
        workflow_state.save_checkpoint("step1", data)
        
        assert len(workflow_state.checkpoints) == 1
        assert workflow_state.state["step1"] == data
    
    def test_get_checkpoint(self, workflow_state):
        """Test getting checkpoint."""
        data = {"result": "test"}
        workflow_state.save_checkpoint("step1", data)
        
        checkpoint = workflow_state.get_checkpoint("step1")
        assert checkpoint == data
    
    def test_get_last_checkpoint(self, workflow_state):
        """Test getting last checkpoint."""
        workflow_state.save_checkpoint("step1", {"result": "step1"})
        workflow_state.save_checkpoint("step2", {"result": "step2"})
        
        last = workflow_state.get_last_checkpoint()
        assert last["step"] == "step2"
    
    def test_can_resume(self, workflow_state):
        """Test resume capability."""
        assert workflow_state.can_resume() is False
        
        workflow_state.save_checkpoint("step1", {})
        assert workflow_state.can_resume() is True
    
    def test_to_dict(self, workflow_state):
        """Test state serialization."""
        workflow_state.save_checkpoint("step1", {"result": "test"})
        
        state_dict = workflow_state.to_dict()
        
        assert state_dict["workflow_id"] == "test-workflow-123"
        assert "checkpoints" in state_dict
        assert "created_at" in state_dict


class TestWorkflowStateManager:
    """Test cases for WorkflowStateManager."""
    
    @pytest.fixture
    def state_manager(self):
        """Create state manager instance."""
        return WorkflowStateManager()
    
    def test_create_workflow_state(self, state_manager):
        """Test creating workflow state."""
        state = state_manager.create_workflow_state()
        
        assert state.workflow_id is not None
        assert state in state_manager.states.values()
    
    def test_create_workflow_state_with_id(self, state_manager):
        """Test creating workflow state with ID."""
        state = state_manager.create_workflow_state("custom-id")
        
        assert state.workflow_id == "custom-id"
        assert state_manager.get_workflow_state("custom-id") == state
    
    def test_save_checkpoint(self, state_manager):
        """Test saving checkpoint."""
        state = state_manager.create_workflow_state("test-id")
        state_manager.save_checkpoint("test-id", "step1", {"result": "test"})
        
        checkpoint = state.get_checkpoint("step1")
        assert checkpoint == {"result": "test"}
    
    def test_restore_from_checkpoint(self, state_manager):
        """Test restoring from checkpoint."""
        state = state_manager.create_workflow_state("test-id")
        state_manager.save_checkpoint("test-id", "step1", {"result": "test"})
        
        data = state_manager.restore_from_checkpoint("test-id", "step1")
        assert data == {"result": "test"}
    
    def test_restore_from_checkpoint_not_found(self, state_manager):
        """Test restoring from non-existent checkpoint."""
        state_manager.create_workflow_state("test-id")
        
        data = state_manager.restore_from_checkpoint("test-id", "step1")
        assert data is None
    
    def test_cleanup_old_states(self, state_manager):
        """Test cleaning up old states."""
        # Create old state
        state = state_manager.create_workflow_state("old-id")
        state.updated_at = datetime(2020, 1, 1)
        
        # Create new state
        state_manager.create_workflow_state("new-id")
        
        state_manager.cleanup_old_states(max_age_hours=1)
        
        assert state_manager.get_workflow_state("old-id") is None
        assert state_manager.get_workflow_state("new-id") is not None
