"""
Workflow Registry

Loads and manages workflow definitions from YAML.
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger

from orchestrator.workflow_config import WorkflowDefinition, WorkflowStep
from orchestrator.exceptions import WorkflowNotFoundError


class WorkflowRegistry:
    """
    Registry for workflow definitions.
    
    Loads workflows from YAML files and provides lookup.
    """
    
    def __init__(self, workflows_file: Optional[str] = None):
        """
        Initialize workflow registry.
        
        Args:
            workflows_file: Path to workflows YAML file
        """
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.workflows_file = workflows_file or "config/workflows.yaml"
        self._load_workflows()
    
    def _load_workflows(self):
        """Load workflows from YAML file."""
        try:
            workflows_path = Path(self.workflows_file)
            if not workflows_path.exists():
                logger.warning(f"Workflows file not found: {self.workflows_file}")
                return
            
            with open(workflows_path, 'r') as f:
                data = yaml.safe_load(f)
            
            workflows_data = data.get("workflows", {})
            
            for workflow_name, workflow_data in workflows_data.items():
                workflow = self._parse_workflow(workflow_name, workflow_data)
                self.workflows[workflow_name] = workflow
            
            logger.info(f"Loaded {len(self.workflows)} workflows")
            
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def _parse_workflow(
        self,
        workflow_name: str,
        workflow_data: Dict
    ) -> WorkflowDefinition:
        """Parse workflow from YAML data."""
        # This is a simplified parser
        # In production, would fully parse all fields
        
        from orchestrator.workflow_config import (
            WorkflowDefinition,
            WorkflowStep,
            RetryConfig,
            ErrorHandling,
            TransactionConfig
        )
        
        steps = []
        for step_data in workflow_data.get("steps", []):
            try:
                # Parse retry_config if present
                retry_config = None
                if "retry_config" in step_data and isinstance(step_data["retry_config"], dict):
                    retry_data = step_data["retry_config"]
                    retry_config = RetryConfig(
                        max_retries=retry_data.get("max_retries", 3),
                        backoff=retry_data.get("backoff", "exponential"),
                        initial_delay=retry_data.get("initial_delay", 1.0)
                    )
                
                # Ensure required fields exist
                if "step" not in step_data:
                    logger.warning(f"Step missing 'step' field in workflow '{workflow_name}', skipping")
                    continue
                
                # Handle workflow references (sub-workflows)
                if "workflow" in step_data:
                    logger.debug(f"Step '{step_data['step']}' references workflow '{step_data['workflow']}' - sub-workflow support not yet implemented, skipping")
                    continue
                
                if "agent" not in step_data:
                    logger.warning(f"Step '{step_data.get('step', 'unknown')}' missing 'agent' field in workflow '{workflow_name}', skipping")
                    continue
                
                step = WorkflowStep(
                    step=step_data["step"],
                    agent=step_data["agent"],
                    input_mapping=step_data.get("input_mapping", {}),
                    parallel=step_data.get("parallel", False),
                    max_concurrent=step_data.get("max_concurrent", 5),
                    rate_limit=step_data.get("rate_limit", 10),
                    retry_config=retry_config,
                    timeout=step_data.get("timeout"),
                    cache=step_data.get("cache", True),
                    cache_ttl=step_data.get("cache_ttl"),
                    conditions=step_data.get("conditions"),
                    filter=step_data.get("filter")
                )
                steps.append(step)
            except KeyError as e:
                logger.error(f"Missing required field in step: {e}, workflow: {workflow_name}")
                continue
            except Exception as e:
                logger.error(f"Error parsing step in workflow '{workflow_name}': {e}")
                continue
        
        error_handling = ErrorHandling(
            on_failure=workflow_data.get("error_handling", {}).get("on_failure", "partial"),
            retry_workflow=workflow_data.get("error_handling", {}).get("retry_workflow", False)
        )
        
        transaction = TransactionConfig(
            enabled=workflow_data.get("transaction", {}).get("enabled", False),
            rollback_on_failure=workflow_data.get("transaction", {}).get("rollback_on_failure", False)
        )
        
        return WorkflowDefinition(
            name=workflow_data.get("name", workflow_name),
            description=workflow_data.get("description", ""),
            version=workflow_data.get("version", "1.0"),
            steps=steps,
            parallel_steps=workflow_data.get("parallel_steps"),
            error_handling=error_handling,
            transaction=transaction
        )
    
    def get(self, workflow_name: str) -> Optional[WorkflowDefinition]:
        """
        Get workflow by name.
        
        Args:
            workflow_name: Name of workflow
        
        Returns:
            WorkflowDefinition or None
        """
        return self.workflows.get(workflow_name)
    
    def register(self, workflow_name: str, workflow: WorkflowDefinition):
        """
        Register a workflow.
        
        Args:
            workflow_name: Name of workflow
            workflow: WorkflowDefinition
        """
        self.workflows[workflow_name] = workflow
        logger.info(f"Registered workflow: {workflow_name}")
    
    def list_workflows(self) -> List[str]:
        """List all workflow names."""
        return list(self.workflows.keys())
    
    def reload(self):
        """Reload workflows from file."""
        self.workflows.clear()
        self._load_workflows()
