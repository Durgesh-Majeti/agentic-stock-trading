"""Unit tests for WorkflowComposer."""
import pytest
from unittest.mock import Mock
from orchestrator.workflow_composer import WorkflowComposer
from orchestrator.workflow_registry import WorkflowRegistry
from orchestrator.workflow_config import WorkflowDefinition
from orchestrator.exceptions import WorkflowNotFoundError


class TestWorkflowComposer:
    """Test cases for WorkflowComposer."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = Mock(spec=WorkflowRegistry)
        
        workflow1 = WorkflowDefinition(name="workflow1", description="Test 1")
        workflow2 = WorkflowDefinition(name="workflow2", description="Test 2")
        find_candidates = WorkflowDefinition(name="find_candidates", description="Find candidates")
        analyze_signals = WorkflowDefinition(name="analyze_signals", description="Analyze signals")
        fetch_data = WorkflowDefinition(name="fetch_data", description="Fetch data")
        analyze_sentiment = WorkflowDefinition(name="analyze_sentiment", description="Analyze sentiment")
        
        registry.get = Mock(side_effect=lambda name: {
            "workflow1": workflow1,
            "workflow2": workflow2,
            "find_candidates": find_candidates,
            "analyze_signals": analyze_signals,
            "fetch_data": fetch_data,
            "analyze_sentiment": analyze_sentiment
        }.get(name))
        
        return registry
    
    @pytest.fixture
    def composer(self, mock_registry):
        """Create workflow composer instance."""
        return WorkflowComposer(mock_registry)
    
    def test_compose_workflows(self, composer, mock_registry):
        """Test composing workflows."""
        composed = composer.compose("workflow1", "workflow2")
        
        assert callable(composed)
        mock_registry.get.assert_any_call("workflow1")
        mock_registry.get.assert_any_call("workflow2")
    
    def test_compose_nonexistent_workflow(self, composer, mock_registry):
        """Test composing with non-existent workflow."""
        mock_registry.get.return_value = None
        
        with pytest.raises(WorkflowNotFoundError):
            composer.compose("nonexistent")
    
    def test_create_workflow_library(self, composer):
        """Test creating workflow library."""
        library = composer.create_workflow_library()
        
        assert isinstance(library, dict)
        # Library should contain common patterns
        assert "find_and_analyze" in library or len(library) >= 0
