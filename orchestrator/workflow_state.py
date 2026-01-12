"""
Workflow State Management

Manages workflow state and checkpoints for resumption.
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from orchestrator.exceptions import WorkflowStateError


class WorkflowState:
    """Represents workflow execution state."""
    
    def __init__(self, workflow_id: str):
        """
        Initialize workflow state.
        
        Args:
            workflow_id: Unique workflow execution ID
        """
        self.workflow_id = workflow_id
        self.state: Dict[str, Any] = {}
        self.checkpoints: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def save_checkpoint(self, step_name: str, data: Dict[str, Any]):
        """
        Save workflow checkpoint.
        
        Args:
            step_name: Name of completed step
            data: Step output data
        """
        checkpoint = {
            "step": step_name,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Remove old checkpoint for same step
        self.checkpoints = [
            cp for cp in self.checkpoints
            if cp["step"] != step_name
        ]
        
        self.checkpoints.append(checkpoint)
        self.state[step_name] = data
        self.updated_at = datetime.now()
        
        logger.debug(f"Checkpoint saved: {step_name} in workflow {self.workflow_id}")
    
    def get_checkpoint(self, step_name: str) -> Optional[Dict[str, Any]]:
        """
        Get checkpoint for step.
        
        Args:
            step_name: Name of step
        
        Returns:
            Checkpoint data or None
        """
        for checkpoint in self.checkpoints:
            if checkpoint["step"] == step_name:
                return checkpoint["data"]
        return None
    
    def get_last_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get last checkpoint."""
        if self.checkpoints:
            return self.checkpoints[-1]
        return None
    
    def can_resume(self) -> bool:
        """Check if workflow can be resumed."""
        return len(self.checkpoints) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "state": self.state,
            "checkpoints": self.checkpoints,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class WorkflowStateManager:
    """
    Manages workflow state persistence.
    
    Note: In production, this would use database.
    For now, uses in-memory storage.
    """
    
    def __init__(self):
        """Initialize state manager."""
        self.states: Dict[str, WorkflowState] = {}
    
    def create_workflow_state(self, workflow_id: Optional[str] = None) -> WorkflowState:
        """
        Create new workflow state.
        
        Args:
            workflow_id: Optional workflow ID (generated if None)
        
        Returns:
            WorkflowState instance
        """
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
        
        state = WorkflowState(workflow_id)
        self.states[workflow_id] = state
        
        logger.debug(f"Created workflow state: {workflow_id}")
        return state
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Get workflow state.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            WorkflowState or None
        """
        return self.states.get(workflow_id)
    
    def save_checkpoint(
        self,
        workflow_id: str,
        step_name: str,
        data: Dict[str, Any]
    ):
        """
        Save workflow checkpoint.
        
        Args:
            workflow_id: Workflow ID
            step_name: Step name
            data: Step data
        """
        state = self.get_workflow_state(workflow_id)
        if not state:
            raise WorkflowStateError(f"Workflow state not found: {workflow_id}")
        
        state.save_checkpoint(step_name, data)
        
        # TODO: Persist to database
        # self._persist_to_database(state)
    
    def restore_from_checkpoint(
        self,
        workflow_id: str,
        step_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Restore workflow from checkpoint.
        
        Args:
            workflow_id: Workflow ID
            step_name: Optional step name (uses last if None)
        
        Returns:
            Checkpoint data or None
        """
        state = self.get_workflow_state(workflow_id)
        if not state:
            return None
        
        if step_name:
            return state.get_checkpoint(step_name)
        else:
            last_checkpoint = state.get_last_checkpoint()
            return last_checkpoint["data"] if last_checkpoint else None
    
    def cleanup_old_states(self, max_age_hours: int = 24):
        """
        Clean up old workflow states.
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for workflow_id, state in self.states.items():
            if state.updated_at.timestamp() < cutoff:
                to_remove.append(workflow_id)
        
        for workflow_id in to_remove:
            del self.states[workflow_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old workflow states")
