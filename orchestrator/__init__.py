"""
Orchestrator Module

Central controller for all agent interactions with 10 improvements:
1. Parallel Execution with Rate Limiting
2. Workflow State Management
3. Workflow Configuration (YAML)
4. Dependency Injection
5. Observability & Monitoring
6. Circuit Breaker Pattern
7. Event-Driven Architecture
8. Transaction Management
9. Caching Layer
10. Workflow Composition
"""

from orchestrator.orchestrator import TradingOrchestrator
from orchestrator.workflow_executor import WorkflowExecutor
from orchestrator.workflow_state import WorkflowStateManager, WorkflowState
from orchestrator.workflow_registry import WorkflowRegistry
from orchestrator.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from orchestrator.cache_manager import CacheManager
from orchestrator.event_bus import EventBus
from orchestrator.transaction_manager import WorkflowTransaction
from orchestrator.monitoring import OrchestratorMonitor
from orchestrator.workflow_composer import WorkflowComposer
from orchestrator.rate_limiter import RateLimiter

__all__ = [
    "TradingOrchestrator",
    "WorkflowExecutor",
    "WorkflowStateManager",
    "WorkflowState",
    "WorkflowRegistry",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CacheManager",
    "EventBus",
    "WorkflowTransaction",
    "TransactionManager",
    "OrchestratorMonitor",
    "WorkflowComposer",
    "RateLimiter",
]

__version__ = "1.2.0"
