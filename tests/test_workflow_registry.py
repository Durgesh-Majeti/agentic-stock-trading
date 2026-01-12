"""Unit tests for WorkflowRegistry."""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from orchestrator.workflow_registry import WorkflowRegistry
from orchestrator.exceptions import WorkflowNotFoundError


class TestWorkflowRegistry:
    """Test cases for WorkflowRegistry."""
    
    @pytest.fixture
    def sample_yaml(self):
        """Sample YAML content."""
        return """
workflows:
  test_workflow:
    name: "Test Workflow"
    description: "A test workflow"
    version: "1.0"
    steps:
      - step: "step1"
        agent: "librarian"
        input_mapping:
          query: "request.query"
    error_handling:
      on_failure: "partial"
    transaction:
      enabled: false
"""
    
    @pytest.fixture
    def registry(self, sample_yaml):
        """Create registry with mock YAML."""
        with patch("builtins.open", mock_open(read_data=sample_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                return WorkflowRegistry(workflows_file="test_workflows.yaml")
    
    def test_load_workflows(self, registry):
        """Test loading workflows from YAML."""
        assert "test_workflow" in registry.list_workflows()
    
    def test_get_workflow(self, registry):
        """Test getting workflow."""
        workflow = registry.get("test_workflow")
        assert workflow is not None
        assert workflow.name == "Test Workflow"
    
    def test_get_nonexistent_workflow(self, registry):
        """Test getting non-existent workflow."""
        workflow = registry.get("nonexistent")
        assert workflow is None
    
    def test_register_workflow(self, registry):
        """Test registering workflow."""
        from orchestrator.workflow_config import WorkflowDefinition
        
        new_workflow = WorkflowDefinition(
            name="New Workflow",
            description="A new workflow"
        )
        
        registry.register("new_workflow", new_workflow)
        
        assert "new_workflow" in registry.list_workflows()
        assert registry.get("new_workflow") == new_workflow
    
    def test_list_workflows(self, registry):
        """Test listing workflows."""
        workflows = registry.list_workflows()
        assert isinstance(workflows, list)
        assert "test_workflow" in workflows
    
    def test_reload(self, registry, sample_yaml):
        """Test reloading workflows."""
        initial_count = len(registry.list_workflows())
        
        # Reload should work with the same mock setup
        with patch("builtins.open", mock_open(read_data=sample_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                registry.reload()
        
        # Should reload workflows
        assert len(registry.list_workflows()) == initial_count
