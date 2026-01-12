"""
Orchestrator Exceptions

Custom exceptions for orchestrator operations.
"""


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass


class WorkflowNotFoundError(OrchestratorError):
    """Workflow not found in registry."""
    pass


class WorkflowExecutionError(OrchestratorError):
    """Error during workflow execution."""
    pass


class AgentNotFoundError(OrchestratorError):
    """Agent not found in registry."""
    pass


class AgentCallError(OrchestratorError):
    """Error calling agent."""
    pass


class ContractValidationError(OrchestratorError):
    """Agent contract validation failed."""
    pass


class CircuitBreakerOpenError(OrchestratorError):
    """Circuit breaker is open."""
    pass


class WorkflowStateError(OrchestratorError):
    """Error with workflow state."""
    pass


class TransactionError(OrchestratorError):
    """Transaction error."""
    pass


class RateLimitExceededError(OrchestratorError):
    """Rate limit exceeded."""
    pass
