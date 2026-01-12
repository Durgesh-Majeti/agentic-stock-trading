# Orchestrator Module

This module implements the central orchestrator for the agentic trading system with **10 key improvements** for production readiness.

## Structure

```
orchestrator/
├── __init__.py                 # Module exports
├── orchestrator.py             # Main orchestrator class
├── workflow_executor.py        # Parallel execution, rate limiting
├── workflow_state.py           # State management & checkpoints
├── workflow_registry.py        # Workflow loading & management
├── workflow_config.py          # Workflow definition classes
├── circuit_breaker.py          # Circuit breaker pattern
├── cache_manager.py            # Caching layer
├── event_bus.py                # Event-driven architecture
├── transaction_manager.py       # Transaction management
├── monitoring.py                # Observability & metrics
├── workflow_composer.py         # Workflow composition
├── rate_limiter.py             # Rate limiting implementation
├── exceptions.py                # Custom exceptions
└── README.md                   # This file
```

## The 10 Improvements

1. **Parallel Execution with Rate Limiting** - `workflow_executor.py`, `rate_limiter.py`
2. **Workflow State Management** - `workflow_state.py`
3. **Workflow Configuration (YAML)** - `workflow_registry.py`, `workflow_config.py`
4. **Dependency Injection** - `orchestrator.py`
5. **Observability & Monitoring** - `monitoring.py`
6. **Circuit Breaker Pattern** - `circuit_breaker.py`
7. **Event-Driven Architecture** - `event_bus.py`
8. **Transaction Management** - `transaction_manager.py`
9. **Caching Layer** - `cache_manager.py`
10. **Workflow Composition** - `workflow_composer.py`

## Usage

```python
from orchestrator import TradingOrchestrator

# Initialize orchestrator
orchestrator = TradingOrchestrator()

# Execute workflow
result = await orchestrator.execute_workflow(
    workflow_name="signal_generation",
    request_data={
        "query": "Find oversold RSI stocks",
        "user_id": 12345
    }
)
```

## Configuration

- Workflows: `config/workflows.yaml`
- Agent Contracts: `config/agent_contracts.yaml`

## Documentation

See [Orchestrator Design Document](../docs/13_ORCHESTRATOR_DESIGN.md) for complete details.

## Implementation Status

- [ ] Core orchestrator class
- [ ] Workflow executor
- [ ] State management
- [ ] Workflow registry
- [ ] Circuit breakers
- [ ] Caching
- [ ] Event bus
- [ ] Transactions
- [ ] Monitoring
- [ ] Workflow composition

See `DEVELOPMENT_TODO.md` Phase 5 for detailed implementation tasks.
