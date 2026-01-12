"""
Workflow Configuration

Data classes for workflow definitions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class RetryConfig:
    """Retry configuration for workflow step."""
    max_retries: int = 3
    backoff: str = "exponential"  # exponential, linear
    initial_delay: float = 1.0


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    enabled: bool = False
    failure_threshold: int = 5
    timeout: int = 60


@dataclass
class WorkflowStep:
    """Defines a single workflow step."""
    step: str
    agent: str
    input_mapping: Dict[str, str]
    parallel: bool = False
    max_concurrent: int = 5
    rate_limit: int = 10
    retry_config: Optional[RetryConfig] = None
    timeout: Optional[int] = None
    cache: bool = True
    cache_ttl: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    filter: Optional[Dict[str, Any]] = None
    circuit_breaker: Optional[CircuitBreakerConfig] = None
    event: Optional[Dict[str, Any]] = None


@dataclass
class ErrorHandling:
    """Error handling configuration."""
    on_failure: str = "partial"  # partial, rollback, continue
    retry_workflow: bool = False
    fallback_strategy: Optional[str] = None


@dataclass
class TransactionConfig:
    """Transaction configuration."""
    enabled: bool = False
    rollback_on_failure: bool = False
    checkpoints: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    name: str
    description: str
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    parallel_steps: Optional[List[List[str]]] = None
    error_handling: ErrorHandling = field(default_factory=ErrorHandling)
    transaction: TransactionConfig = field(default_factory=TransactionConfig)
