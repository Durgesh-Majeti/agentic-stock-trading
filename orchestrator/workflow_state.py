"""
Workflow State Management

Manages workflow state and checkpoints for resumption.
"""

import json
import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
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
        self.checkpoint_index: Dict[str, int] = {}  # O(1) lookup by step_name
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
        
        # Remove old checkpoint for same step if exists
        if step_name in self.checkpoint_index:
            old_index = self.checkpoint_index[step_name]
            self.checkpoints.pop(old_index)
            # Rebuild index after removal
            self.checkpoint_index = {
                cp["step"]: idx for idx, cp in enumerate(self.checkpoints)
            }
        
        # Add new checkpoint
        self.checkpoints.append(checkpoint)
        self.checkpoint_index[step_name] = len(self.checkpoints) - 1
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
        # Use O(1) dictionary lookup instead of O(n) linear search
        if step_name in self.checkpoint_index:
            index = self.checkpoint_index[step_name]
            if index < len(self.checkpoints):
                return self.checkpoints[index]["data"]
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
    For now, uses in-memory storage with automatic cleanup.
    """
    
    def __init__(self, max_states: int = 1000, cleanup_interval_hours: int = 24):
        """
        Initialize state manager.
        
        Args:
            max_states: Maximum number of states to keep in memory
            cleanup_interval_hours: Hours after which states are considered old
        """
        self.states: Dict[str, WorkflowState] = {}
        self.max_states = max_states
        self.cleanup_interval_hours = cleanup_interval_hours
        self.last_cleanup = time.time()
    
    def create_workflow_state(self, workflow_id: Optional[str] = None) -> WorkflowState:
        """
        Create new workflow state.
        
        Args:
            workflow_id: Optional workflow ID (generated if None)
        
        Returns:
            WorkflowState instance
        """
        # Auto-cleanup if needed
        self._auto_cleanup()
        
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
        
        # Enforce max_states limit
        if len(self.states) >= self.max_states:
            # Remove oldest state
            oldest_id = min(
                self.states.keys(),
                key=lambda k: self.states[k].updated_at.timestamp()
            )
            del self.states[oldest_id]
            logger.debug(f"Removed oldest workflow state: {oldest_id} (max_states limit)")
        
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
    
    def _auto_cleanup(self):
        """Automatically clean up old states if cleanup interval has passed."""
        current_time = time.time()
        if current_time - self.last_cleanup > (self.cleanup_interval_hours * 3600):
            self.cleanup_old_states(self.cleanup_interval_hours)
            self.last_cleanup = current_time
    
    def cleanup_old_states(self, max_age_hours: Optional[int] = None):
        """
        Clean up old workflow states.
        
        Args:
            max_age_hours: Maximum age in hours (uses instance default if None)
        """
        max_age = max_age_hours or self.cleanup_interval_hours
        cutoff = datetime.now().timestamp() - (max_age * 3600)
        
        to_remove = []
        for workflow_id, state in self.states.items():
            if state.updated_at.timestamp() < cutoff:
                to_remove.append(workflow_id)
        
        for workflow_id in to_remove:
            del self.states[workflow_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old workflow states")
