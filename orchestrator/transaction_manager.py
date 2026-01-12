"""
Transaction Manager

Manages workflow-level transactions with rollback capability.
"""

import asyncio
import time
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
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
    
    def __init__(self, max_transactions: int = 1000, transaction_ttl_hours: int = 24):
        """
        Initialize transaction manager.
        
        Args:
            max_transactions: Maximum number of transactions to keep in memory
            transaction_ttl_hours: Hours after which transactions are considered stale
        """
        self.transactions: Dict[str, WorkflowTransaction] = {}
        self.transaction_timestamps: Dict[str, float] = {}  # Track creation time
        self.max_transactions = max_transactions
        self.transaction_ttl_hours = transaction_ttl_hours
        self.last_cleanup = time.time()
    
    def begin_transaction(self, workflow_id: str) -> WorkflowTransaction:
        """
        Begin a new transaction.
        
        Args:
            workflow_id: Workflow execution ID
        
        Returns:
            WorkflowTransaction
        """
        # Auto-cleanup if needed
        self._auto_cleanup()
        
        # Enforce max_transactions limit
        if len(self.transactions) >= self.max_transactions:
            # Remove oldest transaction
            oldest_id = min(
                self.transaction_timestamps.keys(),
                key=lambda k: self.transaction_timestamps[k]
            )
            del self.transactions[oldest_id]
            del self.transaction_timestamps[oldest_id]
            logger.debug(f"Removed oldest transaction: {oldest_id} (max_transactions limit)")
        
        transaction = WorkflowTransaction(workflow_id)
        self.transactions[workflow_id] = transaction
        self.transaction_timestamps[workflow_id] = time.time()
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
            if workflow_id in self.transaction_timestamps:
                del self.transaction_timestamps[workflow_id]
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
            if workflow_id in self.transaction_timestamps:
                del self.transaction_timestamps[workflow_id]
            logger.debug(f"Transaction rolled back: {workflow_id}")
    
    def _auto_cleanup(self):
        """Automatically clean up old transactions if cleanup interval has passed."""
        current_time = time.time()
        if current_time - self.last_cleanup > (self.transaction_ttl_hours * 3600):
            self.cleanup()
            self.last_cleanup = current_time
    
    def cleanup(self, max_age_hours: Optional[int] = None):
        """
        Clean up old transactions.
        
        Args:
            max_age_hours: Maximum age in hours (uses instance default if None)
        """
        max_age = max_age_hours or self.transaction_ttl_hours
        cutoff = time.time() - (max_age * 3600)
        
        to_remove = []
        for workflow_id, timestamp in self.transaction_timestamps.items():
            if timestamp < cutoff:
                to_remove.append(workflow_id)
        
        for workflow_id in to_remove:
            if workflow_id in self.transactions:
                del self.transactions[workflow_id]
            if workflow_id in self.transaction_timestamps:
                del self.transaction_timestamps[workflow_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old transactions")
