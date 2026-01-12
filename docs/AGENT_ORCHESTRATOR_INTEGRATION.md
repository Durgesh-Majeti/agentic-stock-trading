# Agent-Orchestrator Integration Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Overview

This guide explains how agents integrate with the orchestrator. The orchestrator is the central controller that manages all agent interactions.

---

## Key Design Principles

### 1. Orchestrator Controls Everything
- **Orchestrator decides**: Which agents to call, when to call them, what data to pass
- **Agents are passive**: They only process what orchestrator sends
- **No direct calls**: Agents don't call each other directly

### 2. Contract-Based Communication
- **Input Contracts**: Defined in `config/agent_contracts.yaml`
- **Output Contracts**: Defined in `config/agent_contracts.yaml`
- **Validation**: Orchestrator validates all inputs/outputs

### 3. Database as Communication Hub
- **Agents write**: Results to database tables
- **Orchestrator reads**: From database for context
- **State persistence**: Workflow state stored in database

---

## Agent Implementation Requirements

### Base Agent Interface

All agents must:

1. **Inherit from `BaseAgent`**
   ```python
   from agents.base_agent import BaseAgent
   
   class DatabaseLibrarian(BaseAgent):
       def __init__(self):
           super().__init__("database_librarian", "database")
   ```

2. **Implement `process()` method**
   ```python
   def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
       """Process input and return output according to contract."""
       # Validate input matches contract
       # Process request
       # Return output matching contract
       return output
   ```

3. **Follow Input/Output Contracts**
   - Input must match schema in `agent_contracts.yaml`
   - Output must match schema in `agent_contracts.yaml`
   - Orchestrator validates both

4. **Write Results to Database**
   - Store results in appropriate tables
   - Use repositories for database operations
   - Log decisions to `agent_decisions` table

---

## How Orchestrator Calls Agents

### Example: Signal Generation Workflow

```python
# Orchestrator workflow execution
async def _signal_generation_workflow(self, request_data: Dict):
    # Step 1: Call Librarian
    librarian_input = {
        "query": request_data["query"],
        "max_results": 15
    }
    librarian_output = await self._call_agent("librarian", librarian_input)
    # ↑ Orchestrator validates input/output against contracts
    
    # Step 2: Call Scraper (parallel for multiple symbols)
    symbols = [r["symbol"] for r in librarian_output["results"]]
    scraper_inputs = [
        {"symbol": symbol, "type": "live", "validate": True}
        for symbol in symbols
    ]
    scraper_outputs = await self.workflow_executor.execute_parallel(
        "scraper",
        scraper_inputs,
        lambda inp: self._call_agent("scraper", inp),
        max_concurrent=5
    )
    # ↑ Parallel execution with rate limiting
    
    # Step 3: Call Strategy (parallel)
    strategy_inputs = [
        {
            "symbol": symbol,
            "market_data": scraper_output["data"],
            "indicators": scraper_output["indicators"],
            "sentiment": sentiment_data.get(symbol, {})
        }
        for symbol, scraper_output in zip(symbols, scraper_outputs)
    ]
    signals = await self.workflow_executor.execute_parallel(
        "strategy",
        strategy_inputs,
        lambda inp: self._call_agent("strategy", inp),
        max_concurrent=3
    )
    
    # Step 4: Call Telegram
    telegram_input = {
        "user_id": request_data["user_id"],
        "signals": signals,
        "message_type": "signals"
    }
    await self._call_agent("telegram", telegram_input)
```

---

## Agent Contract Compliance

### Example: Database Librarian Contract

**Input Contract** (from `agent_contracts.yaml`):
```yaml
librarian:
  input:
    query: string (required)
    max_results: integer (optional, default: 15)
    filters: object (optional)
```

**Agent Implementation**:
```python
def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Orchestrator ensures input matches contract
    query = input_data["query"]  # Required
    max_results = input_data.get("max_results", 15)  # Optional
    filters = input_data.get("filters")  # Optional
    
    # Process...
    sql = self.translate(query)
    results = self.execute(sql)
    
    # Return output matching contract
    return {
        "sql": sql,  # Required
        "results": results,  # Required
        "count": len(results),  # Required
        "execution_time": 0.5  # Optional
    }
```

**Output Contract**:
```yaml
librarian:
  output:
    sql: string (required)
    results: array (required)
    count: integer (required)
    execution_time: float (optional)
```

---

## Data Flow Patterns

### Pattern 1: Orchestrator → Agent → Database → Orchestrator

```
Orchestrator calls Agent
    ↓
Agent processes input
    ↓
Agent writes to database
    ↓
Orchestrator reads from database (for next step)
```

### Pattern 2: Event-Driven (Optional)

```
Agent publishes event
    ↓
Event bus dispatches
    ↓
Other agents subscribe and react
```

---

## Agent Responsibilities

### What Agents DO:
- ✅ Process input from orchestrator
- ✅ Return output matching contract
- ✅ Write results to database
- ✅ Log decisions to `agent_decisions`
- ✅ Publish events (optional)

### What Agents DON'T DO:
- ❌ Call other agents directly
- ❌ Decide which agents to call
- ❌ Manage workflow execution
- ❌ Handle caching (orchestrator does this)
- ❌ Handle rate limiting (orchestrator does this)
- ❌ Handle circuit breakers (orchestrator does this)

---

## Integration Checklist

For each agent implementation:

- [ ] Inherit from `BaseAgent`
- [ ] Implement `process(input_data: Dict) -> Dict` method
- [ ] Verify input matches contract in `agent_contracts.yaml`
- [ ] Verify output matches contract in `agent_contracts.yaml`
- [ ] Write results to database via repositories
- [ ] Log decisions to `agent_decisions` table
- [ ] Handle errors gracefully (return error dict)
- [ ] Add unit tests
- [ ] Test with orchestrator (integration test)
- [ ] Verify contract compliance

---

## Testing Agent-Orchestrator Integration

### Unit Test Example

```python
def test_librarian_with_orchestrator():
    """Test librarian called by orchestrator."""
    orchestrator = TradingOrchestrator()
    orchestrator.agents = {"librarian": DatabaseLibrarian()}
    
    result = await orchestrator._call_agent(
        "librarian",
        {"query": "oversold stocks", "max_results": 10}
    )
    
    assert "sql" in result
    assert "results" in result
    assert "count" in result
```

### Integration Test Example

```python
async def test_signal_generation_workflow():
    """Test complete workflow with real agents."""
    orchestrator = TradingOrchestrator()
    # Initialize with real agents
    orchestrator.agents = {
        "librarian": DatabaseLibrarian(),
        "scraper": DataScraper(),
        "strategy": StrategySpecialist(),
        "telegram": TelegramAssistant()
    }
    
    result = await orchestrator.execute_workflow(
        "signal_generation",
        {"query": "oversold RSI stocks", "user_id": 123}
    )
    
    assert result["status"] == "success"
    assert "signals" in result
```

---

## Common Patterns

### Pattern 1: Agent Reads from Database

```python
def process(self, input_data: Dict) -> Dict:
    symbol = input_data["symbol"]
    
    # Read from database (written by another agent)
    market_data = self.repo.get_latest_market_data(symbol)
    
    # Process...
    return result
```

### Pattern 2: Agent Writes to Database

```python
def process(self, input_data: Dict) -> Dict:
    # Process...
    signal = self.generate_signal(input_data)
    
    # Write to database (other agents can read)
    self.repo.create_signal(signal)
    
    return signal
```

### Pattern 3: Agent Publishes Event

```python
def process(self, input_data: Dict) -> Dict:
    # Process...
    trade = self.execute_trade(input_data)
    
    # Publish event (optional)
    await self.event_bus.publish("trade.executed", {
        "trade_id": trade.id,
        "symbol": trade.symbol
    })
    
    return trade
```

---

## Error Handling

### Agent Error Handling

```python
def process(self, input_data: Dict) -> Dict:
    try:
        # Process...
        return result
    except Exception as e:
        logger.error(f"Agent error: {e}")
        # Return error dict (still matches contract)
        return {
            "error": str(e),
            "status": "failed"
        }
```

### Orchestrator Error Handling

- Circuit breaker prevents repeated calls to failing agents
- Retry logic with exponential backoff
- Fallback strategies
- Error events published to event bus

---

## Summary

**Agent Design**:
- Passive (only process what orchestrator sends)
- Contract-compliant (input/output match schemas)
- Database-integrated (write results, read context)
- Event-capable (optional event publishing)

**Orchestrator Design**:
- Central controller (decides everything)
- Contract validator (validates all inputs/outputs)
- Workflow executor (manages multi-step workflows)
- Performance optimizer (caching, parallel execution, rate limiting)

**Integration**:
- Orchestrator calls agents via `_call_agent()`
- Agents return results matching contracts
- Orchestrator validates and processes results
- Database and events enable indirect communication

---

**See Also**:
- `docs/13_ORCHESTRATOR_DESIGN.md` - Complete orchestrator design
- `config/agent_contracts.yaml` - All agent contracts
- `config/workflows.yaml` - Workflow definitions
