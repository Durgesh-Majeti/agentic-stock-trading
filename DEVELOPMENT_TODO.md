# Development Todo List

**Project**: Agentic Stock Trading System  
**Version**: 1.2.0  
**Last Updated**: January 2025

---

## 📋 Development Order

This todo list follows the logical development order based on dependencies and system architecture.

---

## Phase 1: Foundation & Infrastructure ✅ (COMPLETE)

### 1.1 Database Layer
- [x] Database models (`database/models.py`)
- [x] Database session management (`database/session.py`)
- [x] Database initialization script (`scripts/init_db.py`)
- [x] Database migration system (Alembic setup)
- [x] Database backup script (`scripts/backup_database.py`)
- [x] Database maintenance script (`scripts/maintain_database.py`)
- [x] Database verification script (`scripts/verify_database.py`)

### 1.2 Configuration System
- [x] Settings class (`config/settings.py`)
- [x] Ollama configuration (`config/ollama_config.py`)
- [x] Constants (`config/constants.py`)
- [x] Environment validation script (`scripts/validate_environment.py`)
- [x] Configuration test script (`scripts/test_configuration.py`)

### 1.3 Core Services
- [x] Ollama service (`services/ollama_service.py`)
- [x] Technical indicators (`utils/technical_indicators.py`)
- [x] Validation utilities (`utils/validators.py` - complete)
- [x] Helper utilities (`utils/helpers.py` - complete)
- [x] Logging configuration (`config/logging_config.py` - enhanced with rotation)

### 1.4 Repositories
- [x] Market data repository (`database/repositories/market_data_repo.py`)
- [x] Order repository (`database/repositories/order_repo.py`)
- [x] Trade repository (`database/repositories/trade_repo.py`)
- [x] Portfolio repository (`database/repositories/portfolio_repo.py`)
- [x] Analysis repository (`database/repositories/analysis_repo.py`)
- [x] User action repository (`database/repositories/user_action_repo.py`)
- [x] Sentiment repository (`database/repositories/sentiment_repo.py`)

---

## Phase 2: Data Sources Integration

### 2.1 Shoonya API Integration (Primary)
- [ ] Shoonya API client class (`data_sources/shoonya_client.py`)
  - [ ] Authentication (session-based + TOTP)
  - [ ] Session management (24h expiry handling)
  - [ ] REST API wrapper methods
  - [ ] WebSocket connection manager
  - [ ] Error handling and retry logic
- [ ] Shoonya data service (`services/shoonya_service.py`)
  - [ ] Real-time quote fetching
  - [ ] Historical data fetching
  - [ ] Order placement
  - [ ] Portfolio/positions fetching
- [ ] Shoonya WebSocket handler (`data_sources/shoonya_websocket.py`)
  - [ ] WebSocket connection
  - [ ] Subscribe to instruments (500+)
  - [ ] Real-time data parsing
  - [ ] Data validation (5% deviation check)
  - [ ] Reconnection logic
- [ ] Shoonya test script (`scripts/test_shoonya_connection.py`)

### 2.2 Upstox API Integration (Backup)
- [ ] Upstox API client class (`data_sources/upstox_client.py`)
  - [ ] OAuth 2.0 authentication flow
  - [ ] Access token management (daily expiry at 3:30 AM)
  - [ ] Token refresh mechanism
  - [ ] REST API wrapper methods
- [ ] Upstox data service (`services/upstox_service.py`)
  - [ ] Market data fetching (backup)
  - [ ] Historical data fetching
  - [ ] Order placement (if needed)
- [ ] Upstox test script (`scripts/test_upstox_connection.py`)

### 2.3 yfinance Integration (Historical) ✅ (COMPLETE)
- [x] yfinance data fetcher (`data_sources/yfinance_fetcher.py`)
  - [x] Historical OHLCV data
  - [x] Nifty 500 symbol list fetching from CSV
  - [x] Company information
  - [x] Batch processing with rate limiting
  - [x] Browser-like headers to avoid blocking
- [x] Historical data backfill script (`scripts/backfill_nifty500.py`)
  - [x] Nifty 500 symbol list (from niftyindices.com CSV)
  - [x] 2 years historical data
  - [x] Technical indicators calculation (29 indicators)
  - [x] Batch processing with rate limiting
  - [x] Incremental updates (smart skip logic)
  - [x] Force refresh option
  - [x] Custom date range support
  - [x] Update recent days option
  - [x] Upsert pattern (update existing, insert new)
- [x] Unit tests (`tests/test_yfinance_fetcher.py`)
- [x] Integration tests (`tests/test_backfill_integration.py`)

### 2.4 Data Source Orchestrator ✅ (COMPLETE - Simplified)
- [x] Data source manager (`data_sources/data_source_manager.py`)
  - [x] yfinance integration (primary for now)
  - [x] Data freshness validation (2min requirement)
  - [x] Batch fetching support
  - [x] Error handling and fallback
  - [ ] Primary/backup selection logic (Shoonya/Upstox pending)
  - [ ] Fallback mechanism (Shoonya → Upstox → yfinance) (pending Shoonya/Upstox)
- [x] Unit tests (`tests/test_data_source_manager.py`)

### 2.5 News Sources Integration (For Sentiment Analysis) ✅ (COMPLETE)
- [x] News fetcher module (`data_sources/news_fetcher.py`)
  - [x] RSS feed parser (feedparser integration)
  - [x] Economic Times RSS integration (markets, economy, policy)
  - [x] Moneycontrol RSS integration (latest, markets)
  - [x] Business Standard RSS integration (markets, economy, companies)
  - [x] Livemint RSS integration
  - [x] Financial Express RSS integration
  - [x] BSE corporate announcements RSS feed (replaced NSE API)
  - [x] Yahoo Finance RSS integration
  - [x] Article content extraction and HTML cleaning
  - [x] Date parsing with timezone normalization (naive UTC)
  - [x] Source configuration management
  - [x] Rate limiting and error handling
  - [x] Article deduplication by URL
- [x] News source configuration (`config/news_sources.py`)
  - [x] 12 active news sources configured
  - [x] Source definitions with URLs and categories
  - [x] Fetch frequency configuration
  - [x] Source activation/deactivation
  - [x] BSE RSS feed configuration
  - [x] Helper functions for source management
- [x] Database migration script (`scripts/migrate_add_sentiment_tables.py`)
  - [x] news_articles table with indexes
  - [x] sentiment_scores table with indexes
  - [x] macro_stock_sentiment table with indexes
  - [x] news_sources table
  - [x] All active sources inserted automatically
- [x] News fetch and store script (`scripts/fetch_and_store_news.py`)
  - [x] Per-source tracking for efficient incremental fetching
  - [x] Multiple operation modes (incremental, update-recent, force-refresh)
  - [x] Bulk database operations
  - [x] URL-based deduplication
  - [x] Date range filtering
  - [x] Timezone normalization (naive UTC)
  - [x] Source status monitoring
- [x] News source update script (`scripts/update_news_sources.py`)
  - [x] Add missing sources to database
  - [x] Update existing source configurations
- [x] RSS feed validation script (`scripts/validate_rss_urls.py`)
  - [x] URL accessibility checking
  - [x] RSS parsing validation
  - [x] Article count reporting
- [x] Sentiment repository enhancements (`database/repositories/sentiment_repo.py`)
  - [x] Per-source tracking methods
  - [x] Bulk operations for articles
  - [x] Source status monitoring
  - [x] Smart start date calculation per source
- [x] News fetcher tests (`tests/test_news_fetcher.py`)

---

## Phase 3: Agent Implementation (Orchestrator-Integrated) ⏳

**Design Principle**: All agents are designed to work with the orchestrator. The orchestrator decides which agents to call, what data to pass, and what data to expect. Agents are passive - they only process what the orchestrator sends.

**Key Requirements**:
- All agents must inherit from `BaseAgent`
- All agents must implement `process(input_data: Dict) -> Dict` method
- All agents must comply with input/output contracts in `config/agent_contracts.yaml`
- Agents write results to database (orchestrator reads from database)
- Agents don't call other agents directly
- Agents can publish events to event bus (optional)

**Orchestrator Integration**:
- Orchestrator calls agents via `orchestrator._call_agent(agent_name, input_data)`
- Orchestrator validates input/output against contracts
- Orchestrator handles caching, circuit breakers, rate limiting
- Orchestrator manages workflow execution and state
- See Phase 5 for complete orchestrator implementation

**Note**: All agents are designed to work with the orchestrator. The orchestrator decides which agents to call, what data to pass, and what data to expect. Agents are passive - they only process what the orchestrator sends.

### 3.1 Base Agent Framework ✅
- [x] Base agent class (`agents/base_agent.py`)
  - [x] Abstract `process(input_data: Dict) -> Dict` method (required by orchestrator)
  - [x] Inherit from `ABC` (Abstract Base Class)
  - [x] LLM initialization via OllamaService (based on model_role)
  - [x] Decision logging to `agent_decisions` table
  - [x] Error handling wrapper (`safe_process()` method)
  - [x] Common utilities (validation helpers)
  - [x] Input/output validation helpers
  - [x] Agent name to enum mapping
  - [x] Support for agents without LLM (model_role=None)
- [x] Base agent tests (`tests/test_base_agent.py`)
  - [x] Test LLM initialization (all roles)
  - [x] Test decision logging
  - [x] Test error handling
  - [x] Test abstract interface
  - [x] Test input/output validation
  - [x] Test safe_process wrapper
  - [x] Test agent name enum mapping

### 3.2 Agent #1: Database Librarian ✅
- [x] Database Librarian agent (`agents/database_librarian.py`)
  - [x] Inherit from `BaseAgent` with `model_role="database"`
  - [x] Implement `process(input_data: Dict) -> Dict` method
  - [x] **Input Contract Compliance**: Accept `query`, `max_results`, `filters` (per `agent_contracts.yaml`)
  - [x] **Output Contract Compliance**: Return `sql`, `results`, `count`, `execution_time` (per `agent_contracts.yaml`)
  - [x] Natural language to SQL translation using LLM
  - [x] Schema awareness (load table/column info from database via SQLAlchemy inspector)
  - [x] SQL query generation with LLM (Qwen2.5 Coder)
  - [x] Query validation and safety checks (prevent DROP, DELETE, TRUNCATE, ALTER, CREATE, INSERT, UPDATE, etc.)
  - [x] Query execution on SQLite database (using SQLAlchemy)
  - [x] Result formatting (convert to list of dicts)
  - [x] Log all queries to `agent_decisions` table
- [x] Database Librarian tests (`tests/test_database_librarian.py`)
  - [x] Test NL → SQL translation
  - [x] Test query execution
  - [x] Test input/output contract compliance
  - [x] Test error handling
  - [x] Test schema awareness
  - [x] Test query safety validation
  - [x] Test markdown cleaning from LLM responses
- [ ] Integration with Orchestrator (Pending Phase 5.13)
  - [ ] Verify orchestrator can call agent
  - [ ] Verify input/output matches contracts
  - [ ] Test with workflow executor

### 3.3 Agent #2: Data Scraper
- [ ] Data Scraper agent (`agents/data_scraper.py`)
  - [ ] Inherit from `BaseAgent` (no LLM needed, but use base for logging)
  - [ ] Implement `process(input_data: Dict) -> Dict` method
  - [ ] **Input Contract Compliance**: Accept `symbol`, `type`, `validate`, `calculate_indicators`, `days` (per `agent_contracts.yaml`)
  - [ ] **Output Contract Compliance**: Return `symbol`, `data`, `indicators`, `source`, `valid`, `timestamp` (per `agent_contracts.yaml`)
  - [ ] Multi-source data fetching (Shoonya → Upstox → yfinance fallback)
  - [ ] Data validation (5% price deviation check, 2min freshness requirement)
  - [ ] Technical indicators calculation (29 indicators using `utils/technical_indicators.py`)
  - [ ] Database storage (daily + intraday via `MarketDataRepository`)
  - [ ] Error handling and fallback to backup sources
  - [ ] Log all data fetches to `agent_decisions` table
- [ ] Data Scraper tests (`tests/test_data_scraper.py`)
  - [ ] Test data fetching from each source
  - [ ] Test validation logic
  - [ ] Test fallback mechanism
  - [ ] Test indicator calculation
  - [ ] Test input/output contract compliance
- [ ] Integration with Orchestrator
  - [ ] Verify orchestrator can call agent
  - [ ] Test parallel execution via workflow executor
  - [ ] Test caching integration

### 3.4 Agent #3: Strategy Specialist
- [ ] Strategy Specialist agent (`agents/strategy_specialist.py`)
  - [ ] Inherit from `BaseAgent` with `model_role="strategy"`
  - [ ] Implement `process(input_data: Dict) -> Dict` method
  - [ ] **Input Contract Compliance**: Accept `symbol`, `market_data`, `indicators`, `sentiment`, `portfolio_context` (per `agent_contracts.yaml`)
  - [ ] **Output Contract Compliance**: Return `action`, `symbol`, `entry_price`, `sl_price`, `target_price`, `confidence`, `reasoning`, `risk_reward`, `position_size` (per `agent_contracts.yaml`)
  - [ ] Market data analysis using LLM (DeepSeek R1 7B)
  - [ ] Technical indicator analysis (RSI, MACD, Bollinger, etc.)
  - [ ] Support/resistance identification
  - [ ] Trade signal generation (BUY/SELL/HOLD)
  - [ ] Entry price calculation
  - [ ] Stop loss calculation (2% default)
  - [ ] Target price calculation (4% default)
  - [ ] Confidence score (0-100%)
  - [ ] **Sentiment integration**: Accept sentiment data from orchestrator input
  - [ ] **Sentiment-weighted confidence**: Adjust confidence based on sentiment scores
  - [ ] Risk assessment (portfolio context from orchestrator)
  - [ ] Signal storage in `screening_signals` table via repository
  - [ ] Log all decisions to `agent_decisions` table
- [ ] Strategy Specialist tests (`tests/test_strategy_specialist.py`)
  - [ ] Test signal generation
  - [ ] Test confidence calculation
  - [ ] Test sentiment integration
  - [ ] Test risk assessment
  - [ ] Test input/output contract compliance
  - [ ] Test JSON parsing from LLM
- [ ] Integration with Orchestrator
  - [ ] Verify orchestrator can call agent
  - [ ] Test parallel execution for multiple symbols
  - [ ] Test with sentiment data from News Sentiment Analyst

### 3.5 Agent #4: Telegram Assistant
- [ ] Telegram Assistant agent (`agents/telegram_assistant.py`)
  - [ ] Inherit from `BaseAgent` with `model_role="chatbot"`
  - [ ] Implement `process(input_data: Dict) -> Dict` method
  - [ ] **Input Contract Compliance**: Accept `user_id`, `message_type`, `signals`, `query`, `order`, `message` (per `agent_contracts.yaml`)
  - [ ] **Output Contract Compliance**: Return `sent`, `message_id`, `error` (per `agent_contracts.yaml`)
  - [ ] Command parsing (`/start`, `/status`, `/positions`, `/kill`, `/query`)
  - [ ] Natural language query handling (route to orchestrator)
  - [ ] Trade approval workflow (receive signals from orchestrator)
  - [ ] Inline keyboard generation (approve/reject buttons)
  - [ ] Alert formatting and sending
  - [ ] User interaction via LLM (Gemma2)
  - [ ] Subscribe to event bus for signal notifications
- [ ] Telegram bot handlers (`bot/telegram_handlers.py`)
  - [ ] Command handlers (integrate with orchestrator)
  - [ ] Callback query handlers (approval buttons → orchestrator)
  - [ ] Message handlers (route to orchestrator)
  - [ ] Error handlers
- [ ] Telegram bot service (`services/telegram_service.py`)
  - [ ] Bot initialization
  - [ ] Message sending
  - [ ] Alert broadcasting
  - [ ] Event bus integration
- [ ] Telegram Assistant tests (`tests/test_telegram_assistant.py`)
  - [ ] Test command parsing
  - [ ] Test approval workflow
  - [ ] Test message formatting
  - [ ] Test input/output contract compliance
- [ ] Integration with Orchestrator
  - [ ] Verify orchestrator can call agent
  - [ ] Test event bus subscription
  - [ ] Test workflow integration

### 3.6 Agent #5: News Sentiment Analyst
- [ ] News Sentiment Analyst agent (`agents/news_sentiment_analyst.py`)
  - [ ] Inherit from `BaseAgent` with `model_role="strategy"` (uses DeepSeek R1 7B)
  - [ ] Implement `process(input_data: Dict) -> Dict` method
  - [ ] **Input Contract Compliance**: Accept `symbols`, `lookback_days`, `sources`, `article` (per `agent_contracts.yaml`)
  - [ ] **Output Contract Compliance**: Return `sentiment_scores`, `article_count`, `analyzed_articles` (per `agent_contracts.yaml`)
  - [ ] News fetching from RSS/API sources (use existing `data_sources/news_fetcher.py`)
  - [ ] Article deduplication (by URL)
  - [ ] Article categorization (stock/sector/macro/government/international)
  - [ ] Sentiment analysis using DeepSeek R1 7B
  - [ ] Macro news categorization and sector impact mapping
  - [ ] Macro-to-stock sentiment propagation
  - [ ] Daily sentiment aggregation (stock-specific + sector + macro)
  - [ ] Database storage via `SentimentRepository` (news_articles, sentiment_scores, macro_stock_sentiment)
  - [ ] Log all sentiment analyses to `agent_decisions` table
- [ ] News Sentiment Analyst tests (`tests/test_news_sentiment_analyst.py`)
  - [ ] Test sentiment analysis
  - [ ] Test categorization
  - [ ] Test macro propagation
  - [ ] Test aggregation
  - [ ] Test input/output contract compliance
- [ ] Integration with Orchestrator
  - [ ] Verify orchestrator can call agent
  - [ ] Test parallel execution for multiple symbols
  - [ ] Test integration with Strategy Specialist (sentiment input)

### 3.7 Agent #6: Portfolio Guardian
- [ ] Portfolio Guardian agent (`agents/portfolio_guardian.py`)
  - [ ] Inherit from `BaseAgent` (optional LLM for risk assessment)
  - [ ] Implement `process(input_data: Dict) -> Dict` method
  - [ ] **Input Contract Compliance**: Accept `portfolio_id`, `position`, `trade_id` (per `agent_contracts.yaml`)
  - [ ] **Output Contract Compliance**: Return `positions`, `breached_positions`, `alerts`, `portfolio_heat` (per `agent_contracts.yaml`)
  - [ ] Portfolio monitoring (can be called by orchestrator or run standalone)
  - [ ] Position tracking (read from `trades` table)
  - [ ] Stop loss monitoring (check live prices)
  - [ ] Target monitoring (alert when near target)
  - [ ] Portfolio heat calculation (exposure percentage)
  - [ ] Risk assessment
  - [ ] Alert generation (publish to event bus)
  - [ ] Emergency stop logic
  - [ ] Subscribe to `trade.executed` events from event bus
- [ ] Portfolio Guardian tests (`tests/test_portfolio_guardian.py`)
  - [ ] Test monitoring loop
  - [ ] Test stop loss detection
  - [ ] Test portfolio heat calculation
  - [ ] Test alert generation
  - [ ] Test input/output contract compliance
- [ ] Integration with Orchestrator
  - [ ] Verify orchestrator can call agent
  - [ ] Test event bus subscription
  - [ ] Test standalone monitoring mode (5-minute intervals)

### 3.8 Agent Integration with Orchestrator
- [ ] Create agent factory/registry
  - [ ] Agent registration system
  - [ ] Agent discovery
  - [ ] Agent health checks
- [ ] Verify all agents follow contracts
  - [ ] Validate input schemas match `agent_contracts.yaml`
  - [ ] Validate output schemas match `agent_contracts.yaml`
  - [ ] Test contract validation in orchestrator
- [ ] Integration tests
  - [ ] Test orchestrator calling each agent
  - [ ] Test workflow execution with real agents
  - [ ] Test error handling and recovery
  - [ ] Test parallel execution
  - [ ] Test caching
  - [ ] Test circuit breakers
- [ ] End-to-end workflow tests
  - [ ] Signal generation workflow with real agents
  - [ ] Trade execution workflow with real agents
  - [ ] User query workflow with real agents

### 3.9 Agent Design Principles (All Agents Must Follow)
- [ ] **Passive Design**: Agents only process what orchestrator sends
- [ ] **No Direct Calls**: Agents don't call other agents directly
- [ ] **Database Communication**: Agents write results to database for other agents to read
- [ ] **Contract Compliance**: All agents must follow input/output contracts in `agent_contracts.yaml`
- [ ] **BaseAgent Interface**: All agents inherit from `BaseAgent` and implement `process()` method
- [ ] **Error Handling**: All agents handle errors gracefully and return error dicts
- [ ] **Decision Logging**: All agents log decisions to `agent_decisions` table
- [ ] **Event Publishing**: Agents publish events to event bus (optional, for async communication)

---

## Phase 4: Service Layer

### 4.1 Trading Service
- [ ] Trading service (`services/trading_service.py` - complete)
  - [ ] Order creation from signals
  - [ ] Order execution via Shoonya
  - [ ] Trade creation and logging
  - [ ] Position management
  - [ ] P&L calculation

### 4.2 Approval Service
- [ ] Approval service (`services/approval_service.py` - complete)
  - [ ] Approval workflow
  - [ ] Order status management
  - [ ] User action logging
  - [ ] Approval timeout handling

### 4.3 Analysis Service
- [ ] Analysis service (`services/analysis_service.py` - complete)
  - [ ] Signal aggregation
  - [ ] Agent decision retrieval
  - [ ] Market data aggregation
  - [ ] Performance metrics calculation

### 4.4 Notification Service
- [ ] Notification service (`services/notification_service.py` - complete)
  - [ ] Telegram notifications
  - [ ] Alert formatting
  - [ ] Notification queuing
  - [ ] Rate limiting

---

## Phase 5: Orchestration (With 10 Improvements) ✅ (IMPLEMENTATION COMPLETE)

### 5.1 Core Orchestrator Infrastructure ✅
- [x] Create orchestrator module structure (`orchestrator/`)
  - [x] `orchestrator/__init__.py`
  - [x] `orchestrator/orchestrator.py` - Main orchestrator class
  - [x] `orchestrator/exceptions.py` - Custom exceptions
- [x] Main orchestrator class (`orchestrator/orchestrator.py`)
  - [x] Agent initialization with dependency injection
  - [x] Agent contract loading
  - [x] Workflow routing logic
  - [x] Data transformation methods
  - [x] Output validation methods
  - [x] Graceful shutdown handling
- [x] Agent contracts (`config/agent_contracts.yaml`)
  - [x] Input/output schemas for all agents
  - [x] Validation rules
  - [x] Type definitions

### 5.2 Improvement #1: Parallel Execution with Rate Limiting ✅
- [x] Workflow executor (`orchestrator/workflow_executor.py`)
  - [x] Parallel execution with semaphore
  - [x] Rate limiter implementation (token bucket)
  - [x] Exception handling per task
  - [x] Configurable concurrency limits
- [x] Rate limiter (`orchestrator/rate_limiter.py`)
  - [x] Token bucket algorithm
  - [x] Per-agent rate limits
  - [x] Configurable limits per workflow
- [x] Tests (`tests/test_workflow_executor.py`, `tests/test_rate_limiter.py`)
  - [x] Test parallel execution
  - [x] Test rate limiting
  - [x] Test exception isolation

### 5.3 Improvement #2: Workflow State Management ✅
- [x] Workflow state manager (`orchestrator/workflow_state.py`)
  - [x] WorkflowState class
  - [x] Checkpoint creation and storage
  - [x] State restoration from checkpoints
  - [x] In-memory persistence (database persistence pending)
- [ ] Database migration for workflow state
  - [ ] `workflow_state` table creation
  - [ ] Indexes for performance
- [x] State persistence methods
  - [x] Save checkpoint (in-memory)
  - [x] Load checkpoint (in-memory)
  - [x] Cleanup old checkpoints
- [x] Tests (`tests/test_workflow_state.py`)

### 5.4 Improvement #3: Workflow Configuration (YAML) ✅
- [x] Workflow definition classes (`orchestrator/workflow_config.py`)
  - [x] WorkflowStep dataclass
  - [x] WorkflowDefinition dataclass
  - [x] YAML parser support
- [x] Workflow registry (`orchestrator/workflow_registry.py`)
  - [x] Load workflows from YAML
  - [x] Workflow lookup and caching
  - [x] Workflow validation
- [x] Workflow configuration files (`config/workflows.yaml`)
  - [x] Signal generation workflow
  - [x] Trade execution workflow
  - [x] User query workflow
  - [x] Portfolio monitoring workflow
  - [x] News sentiment update workflow
- [x] Tests (`tests/test_workflow_registry.py`)

### 5.5 Improvement #4: Dependency Injection ✅
- [x] Dependency injection pattern
  - [x] Constructor injection for agents
  - [x] Factory methods for default creation
  - [x] Interface definitions
- [ ] Agent factory (`orchestrator/agent_factory.py`) (Optional - can use default creation)
  - [ ] Create default agents
  - [ ] Create custom agents
  - [ ] Agent lifecycle management
- [x] Tests with mocking (`tests/test_orchestrator.py`)

### 5.6 Improvement #5: Observability & Monitoring ✅
- [x] Orchestrator monitor (`orchestrator/monitoring.py`)
  - [x] Metrics collection (Counter, Histogram)
  - [x] Workflow tracking context manager
  - [x] Agent call tracking
  - [x] Error tracking
- [ ] Metrics export (Future enhancement)
  - [ ] Prometheus-compatible metrics
  - [ ] JSON metrics endpoint
  - [ ] Metrics dashboard integration
- [x] Structured logging
  - [x] Workflow execution logs
  - [x] Agent call logs
  - [x] Error logs with context
- [x] Tests (`tests/test_monitoring.py`)

### 5.7 Improvement #6: Circuit Breaker Pattern ✅
- [x] Circuit breaker (`orchestrator/circuit_breaker.py`)
  - [x] Three states (CLOSED, OPEN, HALF_OPEN)
  - [x] Failure threshold configuration
  - [x] Timeout configuration
  - [x] Automatic recovery
- [x] Per-agent circuit breakers
  - [x] Circuit breaker registry
  - [x] State tracking per agent
- [x] Integration with orchestrator
  - [x] Wrap agent calls with circuit breaker
  - [x] Handle circuit breaker errors
- [x] Tests (`tests/test_circuit_breaker.py`)

### 5.8 Improvement #7: Event-Driven Architecture ✅
- [x] Event bus (`orchestrator/event_bus.py`)
  - [x] Pub/sub pattern implementation
  - [x] Event subscription
  - [x] Event publishing
  - [x] Async event dispatch
- [x] Event types definition
  - [x] `trade.executed`
  - [x] `signal.generated`
  - [x] `workflow.completed`
  - [x] `error.occurred`
- [ ] Event handlers (Pending agent integration)
  - [ ] Guardian subscribes to trade events
  - [ ] Telegram subscribes to signal events
  - [ ] Monitor subscribes to all events
- [x] Tests (`tests/test_event_bus.py`)

### 5.9 Improvement #8: Transaction Management ✅
- [x] Transaction manager (`orchestrator/transaction_manager.py`)
  - [x] WorkflowTransaction class
  - [x] Atomic workflow execution
  - [x] Checkpoint-based rollback
  - [x] State consistency guarantees
- [x] Rollback implementation
  - [x] Rollback strategy per step
  - [x] State restoration
  - [x] Error recovery
- [ ] Integration with workflows (Pending workflow execution implementation)
  - [ ] Transaction boundaries
  - [ ] Commit/rollback logic
- [x] Tests (`tests/test_transaction_manager.py`)

### 5.10 Improvement #9: Caching Layer ✅
- [x] Cache manager (`orchestrator/cache_manager.py`)
  - [x] In-memory cache with TTL
  - [x] Cache key generation
  - [x] LRU eviction for size limits
  - [x] Cache hit/miss tracking
- [x] Cache integration
  - [x] Wrap agent calls with cache
  - [x] Configurable TTL per agent
  - [x] Cache invalidation strategies
- [ ] Optional Redis backend (Future enhancement)
  - [ ] Distributed caching support
  - [ ] Redis connection management
- [x] Tests (`tests/test_cache_manager.py`)

### 5.11 Improvement #10: Workflow Composition ✅
- [x] Workflow composer (`orchestrator/workflow_composer.py`)
  - [x] Compose workflows from sub-workflows
  - [x] Data flow between workflows
  - [x] Reusable workflow patterns
- [x] Sub-workflow definitions
  - [x] Common sub-workflows
  - [x] Workflow library
- [x] Composition examples
  - [x] Complex workflows from simple ones
- [x] Tests (`tests/test_workflow_composer.py`)

### 5.12 Workflow Definitions ✅
- [x] Signal generation workflow (`config/workflows.yaml`)
  - [x] Find candidates (Librarian)
  - [x] Fetch data (Scraper) - parallel
  - [x] Analyze sentiment (Sentiment) - optional
  - [x] Generate signals (Strategy) - parallel
  - [x] Present signals (Telegram)
- [x] Trade execution workflow
  - [x] Validate trade (Strategy)
  - [x] Execute order (Trading Service)
  - [x] Notify user (Telegram)
  - [x] Start monitoring (Guardian)
- [x] User query workflow
  - [x] Route query (Orchestrator)
  - [x] Execute appropriate workflow
  - [x] Return results
- [x] Portfolio monitoring workflow
  - [x] Check positions (Guardian)
  - [x] Generate alerts
  - [x] Execute stop losses
- [x] News sentiment update workflow

### 5.13 Integration & Testing ⏳ (Pending Agent Implementation)
- [ ] Integrate orchestrator with existing agents
  - [ ] Update agent interfaces
  - [ ] Test agent integration
- [ ] End-to-end workflow tests
  - [ ] Signal generation workflow test
  - [ ] Trade execution workflow test
  - [ ] Error recovery tests
- [ ] Performance tests
  - [ ] Load testing
  - [ ] Concurrent workflow execution
  - [ ] Cache effectiveness tests
- [x] Documentation
  - [x] Orchestrator usage guide (`docs/13_ORCHESTRATOR_DESIGN.md`)
  - [x] Workflow definition guide (`config/workflows.yaml`)
  - [x] API reference (in design doc)

### 5.14 Main Entry Point ⏳ (Pending Agent Implementation)
- [ ] Main orchestrator entry point (`main.py`)
  - [ ] Initialize orchestrator with all components
  - [ ] Load workflow configurations
  - [ ] Start background tasks (Guardian, Telegram)
  - [ ] Main event loop
  - [ ] Graceful shutdown handling
- [x] Configuration loading
  - [x] Environment variables (via config/settings.py)
  - [x] Workflow YAML files (`config/workflows.yaml`)
  - [x] Agent contracts (`config/agent_contracts.yaml`)
- [ ] Health checks (Future enhancement)
  - [ ] System health endpoint
  - [ ] Agent health checks
  - [ ] Database connectivity check

---

## Phase 6: User Interface

### 6.1 Telegram Bot
- [ ] Telegram bot application (`bot/telegram_app.py`)
  - [ ] Bot initialization
  - [ ] Handler registration
  - [ ] Error handling
  - [ ] Logging
- [ ] Command implementations
  - [ ] `/start` - Welcome and help
  - [ ] `/status` - System status
  - [ ] `/positions` - Current positions
  - [ ] `/query <question>` - Natural language queries
  - [ ] `/kill` - Emergency stop
  - [ ] `/resume` - Resume trading
- [ ] Inline keyboard handlers
  - [ ] Trade approval buttons
  - [ ] Status buttons
  - [ ] Navigation buttons
- [ ] Alert system
  - [ ] Trade alerts
  - [ ] System alerts
  - [ ] Portfolio alerts
  - [ ] Heartbeat messages (30min)

### 6.2 Streamlit Dashboard
- [ ] Dashboard application (`dashboard/app.py`)
  - [ ] Main dashboard page
  - [ ] Portfolio view
  - [ ] Orders view
  - [ ] Trades view
  - [ ] Performance metrics
  - [ ] System status
- [ ] Plotly charts
  - [ ] Portfolio value chart
  - [ ] P&L chart
  - [ ] Trade history chart
  - [ ] Performance metrics
- [ ] Real-time updates
  - [ ] Auto-refresh mechanism
  - [ ] WebSocket integration (if needed)

---

## Phase 7: Resilience Layer

### 7.1 Heartbeat Monitoring
- [ ] Heartbeat service (`resilience/heartbeat.py`)
  - [ ] 30-minute heartbeat check
  - [ ] System health monitoring
  - [ ] Telegram notification
  - [ ] Logging

### 7.2 Stop Loss Monitoring
- [ ] Stop loss monitor (`resilience/stop_loss_monitor.py`)
  - [ ] 5-minute monitoring loop
  - [ ] Position checking
  - [ ] Stop loss breach detection
  - [ ] Auto-exit on breach
  - [ ] Alert generation

### 7.3 Portfolio Heat Monitoring
- [ ] Portfolio heat monitor (`resilience/portfolio_heat_monitor.py`)
  - [ ] 5-minute monitoring loop
  - [ ] Exposure calculation
  - [ ] Heat threshold check (80%)
  - [ ] Trade blocking on high heat
  - [ ] Alert generation

### 7.4 Scheduler Setup
- [ ] APScheduler configuration
  - [ ] Heartbeat job (30min)
  - [ ] Stop loss job (5min)
  - [ ] Portfolio heat job (5min)
  - [ ] Data update job (5min)
  - [ ] Market hours awareness

---

## Phase 8: Testing & Quality Assurance

### 8.1 Unit Tests
- [ ] Database repository tests
- [ ] Service layer tests
- [ ] Agent tests
- [ ] Utility function tests
- [ ] Technical indicator tests

### 8.2 Integration Tests
- [ ] API integration tests (Shoonya, Upstox)
- [ ] Database integration tests
- [ ] Agent workflow tests
- [ ] End-to-end signal generation test

### 8.3 Test Infrastructure
- [ ] Test fixtures and mocks
- [ ] Test database setup
- [ ] Test data generators
- [ ] CI/CD pipeline setup

---

## Phase 9: Deployment & Operations

### 9.1 Deployment Scripts
- [ ] Production deployment script
- [ ] Environment setup script
- [ ] Service installation (Windows/Linux)
- [ ] PM2/NSSM configuration

### 9.2 Monitoring & Logging
- [ ] Enhanced logging configuration
- [ ] Log rotation setup
- [ ] Health check endpoints
- [ ] Metrics collection

### 9.3 Documentation
- [x] Architecture documentation
- [x] API documentation
- [x] Configuration documentation
- [x] Deployment documentation
- [x] Sentiment Analysis System documentation
- [x] News Fetching and Storage guide (comprehensive)
- [x] Git Workflow guide
- [x] Documentation consolidation (merged redundant files)
- [x] Documentation index updated
- [ ] Code documentation (docstrings)
- [ ] API reference (auto-generated)

---

## Phase 10: Production Readiness

### 10.1 Security
- [ ] Credential encryption
- [ ] API key security
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] Rate limiting

### 10.2 Performance
- [ ] Database query optimization
- [ ] API call optimization
- [ ] Model loading optimization
- [ ] Memory management
- [ ] Caching strategy

### 10.3 Error Handling
- [ ] Comprehensive error handling
- [ ] Graceful degradation
- [ ] Retry mechanisms
- [ ] Error recovery
- [ ] Alert on critical errors

### 10.4 Production Checklist
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Monitoring setup
- [ ] Backup system
- [ ] Rollback procedure
- [ ] Security audit
- [ ] Performance testing
- [ ] Load testing

---

## 📊 Progress Tracking

### Completed ✅
- **Phase 1 Complete**: All foundation components implemented with unit tests
  - Database models and repositories (including sentiment models)
  - Configuration system
  - Ollama service
  - Technical indicators
  - Core service skeletons
  - **Sentiment Repository** - Complete CRUD operations for news and sentiment with per-source tracking
- **Phase 2.3 Complete**: yfinance Integration (Historical)
  - yfinance data fetcher with Nifty 500 symbol list support
  - Historical data backfill script with advanced options
  - Technical indicators calculation (29 indicators)
  - Batch processing with rate limiting
  - Incremental updates and smart skip logic
  - Force refresh, custom date range, and update recent days options
  - Comprehensive unit and integration tests
- **Phase 2.4 Complete**: Data Source Orchestrator (Simplified - yfinance only)
  - Data source manager with yfinance integration
  - Data freshness validation
  - Batch fetching support
  - Unit tests
- **Phase 2.5 Complete**: News Sources Integration (For Sentiment Analysis)
  - News fetcher module with RSS parsing (12 active sources)
  - BSE corporate announcements RSS feed (replaced NSE API)
  - Article content extraction and deduplication
  - Per-source tracking for efficient incremental fetching
  - News fetch and store script with multiple operation modes
  - Timezone normalization (naive UTC)
  - Database migration script for sentiment tables
  - News source update script
  - RSS feed validation script
  - Comprehensive test suite
- **Phase 5 Complete**: Orchestrator Implementation (All 10 Improvements)
  - ✅ Core orchestrator infrastructure (13 implementation files)
  - ✅ All 10 improvements implemented:
    1. Parallel execution with rate limiting
    2. Workflow state management
    3. Workflow configuration (YAML)
    4. Dependency injection
    5. Observability & monitoring
    6. Circuit breaker pattern
    7. Event-driven architecture
    8. Transaction management
    9. Caching layer
    10. Workflow composition
  - ✅ Comprehensive test suite (11 test files, 50+ test cases)
  - ✅ Configuration files (workflows.yaml, agent_contracts.yaml)
  - ✅ Complete documentation (3 docs)
  - ⏳ Pending: Integration with agents (requires Phase 3)
- **Documentation Complete (v1.1.0)**:
  - Merged 3 news documentation files into comprehensive guide
  - Updated all NSE references to BSE
  - Removed 7 redundant documentation files
  - Added Git workflow guide
  - Updated documentation index
  - Added orchestrator design documentation
  - Enhanced troubleshooting guides

### In Progress 🚧
- None currently

### In Progress 🚧
- Phase 5.13: Integration & Testing (Waiting for Phase 3 agent implementation)
- Phase 5.14: Main Entry Point (Waiting for Phase 3 agent implementation)

### Pending ⏳
- Phase 2.1: Shoonya API Integration (Primary)
- Phase 2.2: Upstox API Integration (Backup)
- Phase 3: Agent Implementation (including News Sentiment Analyst)
  - Base agent framework
  - All 6 agents (Database Librarian, Data Scraper, Strategy Specialist, Telegram Assistant, News Sentiment Analyst, Portfolio Guardian)
  - Required before orchestrator integration
- Phase 4: Service Layer
- Phase 6-10: Remaining phases

---

## 🎯 Priority Order Summary

1. **Foundation** (Phase 1) - ✅ Complete infrastructure
2. **Data Sources** (Phase 2) - Partial (yfinance, news complete; Shoonya/Upstox pending)
3. **Agents** (Phase 3) - ⏳ Pending (must integrate with orchestrator)
4. **Services** (Phase 4) - ⏳ Pending
5. **Orchestration** (Phase 5) - ✅ Complete (all 10 improvements implemented)
6. **UI** (Phase 6) - ⏳ Pending
7. **Resilience** (Phase 7) - ⏳ Pending
8. **Testing** (Phase 8) - ⏳ Pending
9. **Deployment** (Phase 9) - ⏳ Pending
10. **Production** (Phase 10) - ⏳ Pending

**Note**: Phase 5 (Orchestration) is complete and ready. Phase 3 (Agents) must be implemented to integrate with the orchestrator. Agents are designed to be passive and work with the orchestrator's contract-based system.

---

## 📝 Notes

- **Dependencies**: Each phase builds on previous phases
- **Parallel Work**: Some items in Phase 2-4 can be done in parallel
- **Testing**: Write tests alongside development
- **Documentation**: Update docs as you develop
- **Incremental**: Build and test incrementally

---

**Last Updated**: January 2025  
**Current Version**: 1.1.0
