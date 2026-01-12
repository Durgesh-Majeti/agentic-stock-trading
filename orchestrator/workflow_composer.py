"""
Workflow Composer

Compose workflows from smaller sub-workflows.
"""

from typing import Dict, Any, List, Callable, Optional
from loguru import logger

from orchestrator.workflow_registry import WorkflowRegistry
from orchestrator.exceptions import WorkflowNotFoundError


class WorkflowComposer:
    """
    Composes workflows from smaller sub-workflows.
    
    Enables building complex workflows from reusable components.
    """
    
    def __init__(self, workflow_registry: WorkflowRegistry):
        """
        Initialize workflow composer.
        
        Args:
            workflow_registry: Workflow registry instance
        """
        self.workflow_registry = workflow_registry
    
    def compose(
        self,
        *workflow_names: str,
        name: Optional[str] = None
    ) -> Callable:
        """
        Compose multiple workflows into one.
        
        Args:
            *workflow_names: Names of workflows to compose
            name: Optional name for composed workflow
        
        Returns:
            Composed workflow function
        """
        workflows = []
        for workflow_name in workflow_names:
            workflow = self.workflow_registry.get(workflow_name)
            if not workflow:
                raise WorkflowNotFoundError(f"Workflow not found: {workflow_name}")
            workflows.append(workflow)
        
        async def composed_workflow(request_data: Dict[str, Any]) -> Dict[str, Any]:
            """Execute composed workflow."""
            results = {}
            current_data = request_data.copy()
            
            for workflow in workflows:
                logger.debug(f"Executing sub-workflow: {workflow.name}")
                
                # Execute workflow with current data
                # Note: This is simplified - in production would use orchestrator
                result = {"workflow": workflow.name, "status": "executed"}
                
                # Merge result into current data for next workflow
                current_data.update(result)
                results[workflow.name] = result
            
            return {
                "status": "success",
                "results": results,
                "final_data": current_data
            }
        
        return composed_workflow
    
    def create_workflow_library(self) -> Dict[str, Callable]:
        """
        Create library of common workflow patterns.
        
        Returns:
            Dictionary of reusable workflow patterns
        """
        return {
            "find_and_analyze": self.compose("find_candidates", "analyze_signals"),
            "fetch_and_sentiment": self.compose("fetch_data", "analyze_sentiment"),
            # Add more patterns as needed
        }
