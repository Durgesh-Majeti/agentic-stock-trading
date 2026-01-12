# Orchestrator Design Document

**Version**: 2.0  
**Last Updated**: January 2025  
**Status**: Design Complete - Implementation Pending

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Architecture](#architecture)
4. [The 10 Improvements](#the-10-improvements)
5. [Component Details](#component-details)
6. [Workflow Definitions](#workflow-definitions)
7. [Data Contracts](#data-contracts)
8. [Error Handling](#error-handling)
9. [Performance & Scalability](#performance--scalability)
10. [Implementation Guide](#implementation-guide)

---

## Overview

The **Trading Orchestrator** is the central controller of the agentic trading system. It decides which agents to call, what data to pass, and what data to expect. All agent interactions flow through the orchestrator, ensuring centralized control, observability, and resilience.

### Key Responsibilities

1. **Agent Management**: Initializes, manages, and coordinates all agents
2. **Workflow Execution**: Executes predefined and dynamic workflows
3. **Data Transformation**: Formats data for each agent according to contracts
4. **Output Validation**: Validates agent outputs against schemas
5. **Error Recovery**: Handles failures with retries, circuit breakers, and fallbacks
6. **State Management**: Tracks workflow state and enables resumption
7. **Performance Optimization**: Parallel execution, caching, rate limiting
8. **Observability**: Metrics, logging, and monitoring

---

## Core Principles

### 1. Orchestrator Decides Everything
- **Which agents to call**: Based on workflow definition
- **When to call them**: Sequential or parallel execution
- **What data to pass**: Formatted according to agent contracts
- **What data to expect**: Validated against output schemas

### 2. Agents are Passive
- Agents only process what orchestrator sends
- No direct agent-to-agent communication
- Agents don't know about other agents
- All communication flows through orchestrator

### 3. Database as Communication Hub
- Agents write results to database
- Orchestrator reads from database for context
- State persisted for recovery
- Audit trail maintained

### 4. Configuration-Driven
- Workflows defined in YAML
- Agent contracts in configuration
- Retry policies configurable
- Rate limits configurable

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING ORCHESTRATOR                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Core Orchestrator (orchestrator.py)         │   │
│  │  - Workflow routing                                  │   │
│  │  - Agent coordination                                │   │
│  │  - Dependency injection                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Workflow    │  │   Circuit    │  │    Cache    │     │
│  │  Executor    │  │   Breaker    │  │   Manager   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Workflow   │  │   Event      │  │ Transaction  │     │
│  │   State      │  │    Bus       │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Workflow    │  │ Monitoring   │  │  Workflow   │     │
│  │  Registry    │  │   & Metrics  │  │  Composer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         AGENT LAYER                  │
        │  Librarian | Scraper | Strategy      │
        │  Telegram | Sentiment | Guardian     │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         DATABASE LAYER                │
        │  SQLite (State, Results, Audit)       │
        └───────────────────────────────────────┘
```

---

## The 10 Improvements

### 1. Parallel Execution with Rate Limiting ✅

**Problem**: Sequential execution is slow; orchestrator becomes bottleneck.

**Solution**: Parallel execution with configurable concurrency and rate limiting.

**Implementation**:
- `WorkflowExecutor` class handles parallel execution
- Semaphore-based concurrency control
- Token bucket rate limiting
- Exception handling per task

**Benefits**:
- 5-10x faster for batch operations
- Respects API rate limits
- Prevents resource exhaustion

---

### 2. Workflow State Management ✅

**Problem**: No persistent state; workflows can't resume after failures.

**Solution**: Checkpoint-based state management with database persistence.

**Implementation**:
- `WorkflowState` class manages state
- Checkpoints saved after each step
- State stored in `workflow_state` table
- Resume capability from last checkpoint

**Benefits**:
- Workflows can resume after crashes
- Long-running workflows supported
- Debugging easier with state snapshots

---

### 3. Workflow Configuration (Not Hardcoded) ✅

**Problem**: Workflows hardcoded; difficult to modify without code changes.

**Solution**: YAML-based workflow definitions with runtime loading.

**Implementation**:
- Workflows defined in `config/workflows.yaml`
- `WorkflowDefinition` dataclass for structure
- `WorkflowRegistry` loads and manages workflows
- Dynamic workflow composition

**Benefits**:
- Modify workflows without code changes
- Version control for workflows
- Easy to test different configurations

---

### 4. Dependency Injection ✅

**Problem**: Agents hardcoded; difficult to test and mock.

**Solution**: Dependency injection pattern for all components.

**Implementation**:
- Constructor injection for agents
- Factory methods for default creation
- Easy mocking in tests
- Flexible agent swapping

**Benefits**:
- Testable components
- Easy to swap implementations
- Better separation of concerns

---

### 5. Observability & Monitoring ✅

**Problem**: Limited visibility into orchestrator operations.

**Solution**: Comprehensive metrics, logging, and monitoring.

**Implementation**:
- `OrchestratorMonitor` tracks metrics
- Prometheus-compatible metrics
- Structured logging
- Performance tracking per agent

**Benefits**:
- Real-time system health
- Performance optimization insights
- Debugging support

---

### 6. Circuit Breaker Pattern ✅

**Problem**: No protection against cascading failures.

**Solution**: Circuit breaker prevents repeated calls to failing agents.

**Implementation**:
- `CircuitBreaker` class with three states (CLOSED, OPEN, HALF_OPEN)
- Configurable failure threshold
- Automatic recovery after timeout
- Per-agent circuit breakers

**Benefits**:
- Prevents cascading failures
- Faster failure detection
- Automatic recovery

---

### 7. Event-Driven Architecture ✅

**Problem**: Everything request-driven; some workflows should be event-driven.

**Solution**: Event bus for asynchronous, decoupled communication.

**Implementation**:
- `EventBus` for pub/sub pattern
- Event types: `trade.executed`, `signal.generated`, etc.
- Subscribers register handlers
- Async event processing

**Benefits**:
- Decoupled components
- Background processing
- Scalable architecture

---

### 8. Transaction Management ✅

**Problem**: No transaction boundaries; partial failures leave inconsistent state.

**Solution**: Workflow-level transactions with rollback capability.

**Implementation**:
- `WorkflowTransaction` manages atomic workflows
- Checkpoint-based rollback
- All-or-nothing execution
- State consistency guaranteed

**Benefits**:
- Data consistency
- Rollback on failures
- Reliable workflows

---

### 9. Caching Layer ✅

**Problem**: No caching; repeated calls waste resources.

**Solution**: Multi-level caching with TTL and invalidation.

**Implementation**:
- `CacheManager` with in-memory cache
- TTL-based expiration
- Cache key generation from inputs
- Optional Redis backend for distributed caching

**Benefits**:
- Reduced API calls
- Faster response times
- Lower resource usage

---

### 10. Workflow Composition ✅

**Problem**: Workflows can't be composed; code duplication.

**Solution**: Workflow composition from smaller sub-workflows.

**Implementation**:
- `WorkflowComposer` for composition
- Sub-workflows as building blocks
- Data flow between workflows
- Reusable workflow patterns

**Benefits**:
- DRY principle
- Modular workflows
- Easy to build complex workflows

---

## Component Details

### Core Orchestrator (`orchestrator/orchestrator.py`)

**Main class**: `TradingOrchestrator`

```python
class TradingOrchestrator:
    """
    Central controller for all agent interactions.
    
    Responsibilities:
    - Agent initialization and management
    - Workflow execution
    - Data transformation
    - Output validation
    - Error recovery
    """
    
    def __init__(
        self,
        agents: Optional[Dict[str, BaseAgent]] = None,
        workflow_registry: Optional[WorkflowRegistry] = None,
        state_manager: Optional[WorkflowStateManager] = None,
        cache_manager: Optional[CacheManager] = None,
        event_bus: Optional[EventBus] = None,
        monitor: Optional[OrchestratorMonitor] = None
    ):
        # Dependency injection
        self.agents = agents or self._create_default_agents()
        self.workflow_registry = workflow_registry or WorkflowRegistry()
        self.state_manager = state_manager or WorkflowStateManager()
        self.cache_manager = cache_manager or CacheManager()
        self.event_bus = event_bus or EventBus()
        self.monitor = monitor or OrchestratorMonitor()
        
        # Circuit breakers per agent
        self.circuit_breakers = {
            name: CircuitBreaker() for name in self.agents.keys()
        }
        
        # Agent contracts
        self.agent_contracts = self._load_agent_contracts()
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        request_data: Dict
    ) -> Dict:
        """Execute a workflow by name."""
        workflow = self.workflow_registry.get(workflow_name)
        workflow_id = str(uuid.uuid4())
        
        with self.monitor.track_workflow(workflow_name):
            return await self._execute_workflow_steps(
                workflow, 
                request_data, 
                workflow_id
            )
```

### Workflow Executor (`orchestrator/workflow_executor.py`)

**Handles parallel execution with rate limiting**

```python
class WorkflowExecutor:
    """Executes workflow steps with parallelization and rate limiting."""
    
    async def execute_parallel(
        self,
        agent_name: str,
        inputs: List[Dict],
        max_concurrent: int = 5,
        rate_limit: int = 10
    ) -> List[Dict]:
        """Execute agent calls in parallel with rate limiting."""
        semaphore = asyncio.Semaphore(max_concurrent)
        rate_limiter = RateLimiter(rate_limit)
        
        async def bounded_call(input_data):
            async with semaphore:
                await rate_limiter.acquire()
                return await self._call_agent(agent_name, input_data)
        
        tasks = [bounded_call(inp) for inp in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Agent call failed: {result}")
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
```

### Workflow State Manager (`orchestrator/workflow_state.py`)

**Manages workflow state persistence**

```python
class WorkflowStateManager:
    """Manages workflow state and checkpoints."""
    
    def create_workflow_state(self, workflow_id: str) -> WorkflowState:
        """Create new workflow state."""
        return WorkflowState(workflow_id)
    
    def save_checkpoint(
        self, 
        workflow_id: str, 
        step_name: str, 
        data: Dict
    ):
        """Save workflow checkpoint to database."""
        checkpoint = {
            "workflow_id": workflow_id,
            "step": step_name,
            "data": json.dumps(data),
            "timestamp": datetime.now()
        }
        # Store in workflow_state table
        self._store_in_database(checkpoint)
    
    def restore_from_checkpoint(
        self, 
        workflow_id: str, 
        step_name: str
    ) -> Optional[Dict]:
        """Restore workflow from checkpoint."""
        checkpoint = self._load_from_database(workflow_id, step_name)
        if checkpoint:
            return json.loads(checkpoint["data"])
        return None
```

### Circuit Breaker (`orchestrator/circuit_breaker.py`)

**Prevents cascading failures**

```python
class CircuitBreaker:
    """Circuit breaker pattern for agent calls."""
    
    def __init__(
        self, 
        failure_threshold: int = 5, 
        timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self.timeout} seconds"
                )
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN
            if self.state == "HALF_OPEN":
                self.half_open_calls += 1
                if self.half_open_calls >= self.half_open_max_calls:
                    self.state = "CLOSED"
                    self.failure_count = 0
            elif self.state == "CLOSED":
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(
                    f"Circuit breaker OPEN after {self.failure_count} failures"
                )
            
            raise
```

### Cache Manager (`orchestrator/cache_manager.py`)

**Multi-level caching**

```python
class CacheManager:
    """Manages caching for agent outputs."""
    
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self.cache = {}
        self.ttl = ttl
        self.max_size = max_size
    
    def get_cache_key(self, agent_name: str, input_data: Dict) -> str:
        """Generate cache key from agent name and input."""
        import hashlib
        key_data = f"{agent_name}:{json.dumps(input_data, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_call(
        self,
        agent_name: str,
        input_data: Dict,
        call_func: Callable
    ) -> Dict:
        """Get from cache or call agent."""
        cache_key = self.get_cache_key(agent_name, input_data)
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age = time.time() - cached["timestamp"]
            if age < self.ttl:
                logger.debug(f"Cache hit for {agent_name}")
                return cached["data"]
            else:
                # Expired - remove
                del self.cache[cache_key]
        
        # Cache miss - call agent
        logger.debug(f"Cache miss for {agent_name}")
        result = await call_func(agent_name, input_data)
        
        # Store in cache (with size limit)
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            "data": result,
            "timestamp": time.time()
        }
        
        return result
```

### Event Bus (`orchestrator/event_bus.py`)

**Event-driven communication**

```python
class EventBus:
    """Event bus for pub/sub pattern."""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_queue = asyncio.Queue()
        self.running = False
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed {handler.__name__} to {event_type}")
    
    async def publish(self, event_type: str, event_data: Dict):
        """Publish event to all subscribers."""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now()
        }
        
        # Async dispatch to all subscribers
        tasks = []
        for handler in self.subscribers[event_type]:
            tasks.append(handler(event_data))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(f"Published event {event_type} to {len(tasks)} subscribers")
```

### Monitoring (`orchestrator/monitoring.py`)

**Observability and metrics**

```python
class OrchestratorMonitor:
    """Tracks orchestrator performance and health."""
    
    def __init__(self):
        self.metrics = {
            "workflow_executions": Counter(),
            "agent_calls": Counter(),
            "errors": Counter(),
            "durations": Histogram(),
            "cache_hits": Counter(),
            "cache_misses": Counter()
        }
        self.start_times = {}
    
    def track_workflow(self, workflow_name: str):
        """Context manager for workflow tracking."""
        return WorkflowTracker(workflow_name, self.metrics)
    
    def track_agent_call(
        self, 
        agent_name: str, 
        duration: float, 
        success: bool
    ):
        """Track agent call metrics."""
        self.metrics["agent_calls"].labels(agent=agent_name).inc()
        self.metrics["durations"].labels(agent=agent_name).observe(duration)
        if not success:
            self.metrics["errors"].labels(agent=agent_name).inc()
    
    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            "workflow_executions": self.metrics["workflow_executions"].values(),
            "agent_calls": self.metrics["agent_calls"].values(),
            "errors": self.metrics["errors"].values(),
            "avg_durations": {
                agent: self.metrics["durations"].labels(agent=agent).mean()
                for agent in ["librarian", "scraper", "strategy", "telegram"]
            }
        }
```

---

## Workflow Definitions

### YAML Configuration (`config/workflows.yaml`)

```yaml
workflows:
  signal_generation:
    name: "Signal Generation"
    description: "Generate trading signals from user query"
    steps:
      - step: "find_candidates"
        agent: "librarian"
        input_mapping:
          query: "request.query"
          max_results: "request.max_results || 15"
        retry_config:
          max_retries: 3
          backoff: "exponential"
        timeout: 30
      
      - step: "fetch_data"
        agent: "scraper"
        input_mapping:
          symbol: "previous.candidates[*].symbol"
        parallel: true
        max_concurrent: 5
        rate_limit: 10
        retry_config:
          max_retries: 2
          backoff: "linear"
        timeout: 60
      
      - step: "analyze_sentiment"
        agent: "sentiment"
        input_mapping:
          symbols: "previous.candidates[*].symbol"
          lookback_days: 1
        conditions:
          include_sentiment: true
        timeout: 120
      
      - step: "generate_signals"
        agent: "strategy"
        input_mapping:
          symbol: "previous.candidates[*].symbol"
          market_data: "fetch_data.data"
          indicators: "fetch_data.indicators"
          sentiment: "analyze_sentiment.sentiment_scores"
        parallel: true
        max_concurrent: 3
        retry_config:
          max_retries: 2
        timeout: 180
      
      - step: "present_signals"
        agent: "telegram"
        input_mapping:
          user_id: "request.user_id"
          signals: "generate_signals.signals"
          query: "request.query"
        timeout: 10
    
    error_handling:
      on_failure: "partial"  # partial, rollback, continue
      retry_workflow: false
    
    parallel_steps:
      - ["fetch_data", "analyze_sentiment"]  # Can run in parallel
  
  trade_execution:
    name: "Trade Execution"
    description: "Execute approved trade"
    steps:
      - step: "validate_trade"
        agent: "strategy"
        input_mapping:
          signal_id: "request.signal_id"
        timeout: 10
      
      - step: "execute_order"
        agent: "trading_service"
        input_mapping:
          signal: "validate_trade.signal"
        retry_config:
          max_retries: 3
        timeout: 30
      
      - step: "notify_user"
        agent: "telegram"
        input_mapping:
          user_id: "request.user_id"
          order: "execute_order.order"
        timeout: 10
      
      - step: "start_monitoring"
        agent: "guardian"
        input_mapping:
          trade_id: "execute_order.trade_id"
        timeout: 5
    
    error_handling:
      on_failure: "rollback"
      retry_workflow: false
```

---

## Data Contracts

### Agent Input/Output Schemas

Defined in `config/agent_contracts.yaml`:

```yaml
agents:
  librarian:
    input:
      query: string (required)
      max_results: integer (optional, default: 15)
      filters: object (optional)
    output:
      sql: string (required)
      results: array (required)
      count: integer (required)
  
  scraper:
    input:
      symbol: string (required)
      type: string (required, enum: [live, historical])
      validate: boolean (optional, default: true)
      calculate_indicators: boolean (optional, default: true)
    output:
      symbol: string (required)
      data: object (required)
      indicators: object (required)
      source: string (required)
      valid: boolean (required)
      timestamp: datetime (required)
  
  strategy:
    input:
      symbol: string (required)
      market_data: object (required)
      indicators: object (required)
      sentiment: object (optional)
      portfolio_context: object (optional)
    output:
      action: string (required, enum: [BUY, SELL, HOLD])
      symbol: string (required)
      entry_price: float (required)
      sl_price: float (required)
      target_price: float (required)
      confidence: float (required, range: [0, 100])
      reasoning: string (required)
      risk_reward: float (required)
```

---

## Error Handling

### Error Recovery Strategies

1. **Retry with Backoff**
   - Exponential backoff for transient failures
   - Linear backoff for rate limits
   - Max retries configurable per step

2. **Circuit Breaker**
   - Prevents cascading failures
   - Automatic recovery after timeout
   - Per-agent circuit breakers

3. **Fallback Strategies**
   - Backup data sources (Shoonya → Upstox → yfinance)
   - Default responses (HOLD signal on strategy failure)
   - Graceful degradation

4. **Workflow Rollback**
   - Transaction-based workflows
   - Checkpoint-based rollback
   - State consistency guaranteed

---

## Performance & Scalability

### Optimization Strategies

1. **Parallel Execution**
   - Configurable concurrency per workflow step
   - Semaphore-based resource control
   - Exception isolation per task

2. **Caching**
   - TTL-based cache expiration
   - LRU eviction for size limits
   - Cache key generation from inputs

3. **Rate Limiting**
   - Token bucket algorithm
   - Per-agent rate limits
   - Configurable limits per workflow

4. **Resource Management**
   - Sequential model loading (RAM constraint)
   - Connection pooling
   - Async I/O throughout

---

## Implementation Guide

### Phase 1: Core Infrastructure
1. Create orchestrator module structure
2. Implement base orchestrator class
3. Implement dependency injection
4. Create agent contracts

### Phase 2: Execution Layer
5. Implement workflow executor (parallel execution)
6. Implement rate limiting
7. Implement circuit breakers
8. Add caching layer

### Phase 3: State & Configuration
9. Implement workflow state management
10. Create workflow configuration system (YAML)
11. Implement workflow registry
12. Add workflow composition

### Phase 4: Advanced Features
13. Implement event bus
14. Add transaction management
15. Implement monitoring & metrics
16. Add observability dashboard

### Phase 5: Integration
17. Integrate with existing agents
18. Create workflow definitions
19. Add tests
20. Performance tuning

---

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies
- Test error handling

### Integration Tests
- Test complete workflows
- Test error recovery
- Test state persistence

### Performance Tests
- Load testing
- Concurrent workflow execution
- Cache effectiveness

---

## Monitoring & Observability

### Metrics Tracked
- Workflow execution count
- Agent call count and duration
- Error rates per agent
- Cache hit/miss ratios
- Circuit breaker state changes

### Logging
- Structured logging (JSON)
- Workflow execution logs
- Agent call logs
- Error logs with stack traces

### Dashboards
- Real-time metrics dashboard
- Workflow execution timeline
- Agent performance metrics
- Error rate trends

---

**Next Steps**: See `DEVELOPMENT_TODO.md` Phase 5 for implementation tasks.
