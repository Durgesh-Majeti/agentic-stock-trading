"""
Transaction Manager

Manages workflow-level transactions with rollback capability.
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from loguru import logger

from orchestrator.exceptions import TransactionError


class WorkflowTransaction:
    """Represents a workflow transaction."""
    
    def __init__(self, workflow_id: str):
        """
        Initialize transaction.
        
        Args:
            workflow_id: Workflow execution ID
        """
        self.workflow_id = workflow_id
        self.executed_steps: List[Dict[str, Any]] = []
        self.rollback_functions: List[Callable] = []
    
    def add_step(
        self,
        step_name: str,
        result: Dict[str, Any],
        rollback_func: Optional[Callable] = None
    ):
        """
        Add executed step to transaction.
        
        Args:
            step_name: Name of step
            result: Step result
            rollback_func: Optional rollback function
        """
        self.executed_steps.append({
            "step": step_name,
            "result": result
        })
        if rollback_func:
            self.rollback_functions.append(rollback_func)
    
    async def rollback(self):
        """Rollback all executed steps."""
        logger.warning(f"Rolling back transaction: {self.workflow_id}")
        
        # Execute rollback functions in reverse order
        for rollback_func in reversed(self.rollback_functions):
            try:
                if asyncio.iscoroutinefunction(rollback_func):
                    await rollback_func()
                else:
                    rollback_func()
            except Exception as e:
                logger.error(f"Rollback function failed: {e}")


class TransactionManager:
    """
    Manages workflow-level transactions.
    
    Provides atomic workflow execution with rollback capability.
    """
    
    def __init__(self):
        """Initialize transaction manager."""
        self.transactions: Dict[str, WorkflowTransaction] = {}
    
    def begin_transaction(self, workflow_id: str) -> WorkflowTransaction:
        """
        Begin a new transaction.
        
        Args:
            workflow_id: Workflow execution ID
        
        Returns:
            WorkflowTransaction
        """
        transaction = WorkflowTransaction(workflow_id)
        self.transactions[workflow_id] = transaction
        logger.debug(f"Transaction begun: {workflow_id}")
        return transaction
    
    def get_transaction(self, workflow_id: str) -> Optional[WorkflowTransaction]:
        """
        Get transaction by ID.
        
        Args:
            workflow_id: Workflow execution ID
        
        Returns:
            WorkflowTransaction or None
        """
        return self.transactions.get(workflow_id)
    
    async def commit(self, workflow_id: str):
        """
        Commit transaction.
        
        Args:
            workflow_id: Workflow execution ID
        """
        transaction = self.get_transaction(workflow_id)
        if transaction:
            # Transaction successful - remove from tracking
            del self.transactions[workflow_id]
            logger.debug(f"Transaction committed: {workflow_id}")
    
    async def rollback(self, workflow_id: str):
        """
        Rollback transaction.
        
        Args:
            workflow_id: Workflow execution ID
        """
        transaction = self.get_transaction(workflow_id)
        if transaction:
            await transaction.rollback()
            del self.transactions[workflow_id]
            logger.debug(f"Transaction rolled back: {workflow_id}")
    
    def cleanup(self):
        """Clean up old transactions."""
        # In production, would clean up based on age
        pass
