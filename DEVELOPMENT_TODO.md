# Development Todo List

**Project**: Agentic Stock Trading System  
**Version**: 1.1.0  
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

## Phase 3: Agent Implementation

### 3.1 Base Agent Framework
- [ ] Base agent class (`agents/base_agent.py`)
  - [ ] Abstract process method
  - [ ] LLM initialization
  - [ ] Decision logging
  - [ ] Error handling
  - [ ] Common utilities

### 3.2 Agent #1: Database Librarian
- [ ] Database Librarian agent (`agents/database_librarian.py`)
  - [ ] Natural language to SQL translation
  - [ ] Schema awareness (table/column knowledge)
  - [ ] SQL query generation with LLM
  - [ ] Query validation and safety checks
  - [ ] Query execution
  - [ ] Result formatting
- [ ] Database Librarian tests
- [ ] Integration with CrewAI

### 3.3 Agent #2: Data Scraper
- [ ] Data Scraper agent (`agents/data_scraper.py`)
  - [ ] Multi-source data fetching
  - [ ] Data validation (5% price deviation check)
  - [ ] Data freshness check (2min requirement)
  - [ ] Technical indicators calculation (29 indicators)
  - [ ] Database storage (daily + intraday)
  - [ ] Error handling and fallback
- [ ] Data Scraper tests
- [ ] Integration with CrewAI

### 3.4 Agent #3: Strategy Specialist
- [ ] Strategy Specialist agent (`agents/strategy_specialist.py`)
  - [ ] Market data analysis
  - [ ] Technical indicator analysis (RSI, MACD, Bollinger, etc.)
  - [ ] Support/resistance identification
  - [ ] Trade signal generation (BUY/SELL/HOLD)
  - [ ] Entry price calculation
  - [ ] Stop loss calculation (2% default)
  - [ ] Target price calculation (4% default)
  - [ ] Confidence score (0-100%)
  - [ ] Risk assessment
  - [ ] **Sentiment integration**: Accept sentiment data as input
  - [ ] **Sentiment-weighted confidence**: Adjust confidence based on sentiment
  - [ ] Signal storage in database
- [ ] Strategy Specialist tests
- [ ] Integration with CrewAI

### 3.5 Agent #4: Telegram Assistant
- [ ] Telegram Assistant agent (`agents/telegram_assistant.py`)
  - [ ] Command parsing (`/start`, `/status`, `/positions`, `/kill`, `/query`)
  - [ ] Natural language query handling
  - [ ] Trade approval workflow
  - [ ] Inline keyboard generation
  - [ ] Alert formatting and sending
  - [ ] User interaction via LLM
- [ ] Telegram bot handlers (`bot/telegram_handlers.py`)
  - [ ] Command handlers
  - [ ] Callback query handlers (approval buttons)
  - [ ] Message handlers
  - [ ] Error handlers
- [ ] Telegram bot service (`services/telegram_service.py`)
  - [ ] Bot initialization
  - [ ] Message sending
  - [ ] Alert broadcasting
- [ ] Telegram Assistant tests
- [ ] Integration with CrewAI

### 3.5 Agent #5: News Sentiment Analyst
- [ ] News Sentiment Analyst agent (`agents/news_sentiment_analyst.py`)
  - [ ] News fetching from RSS/API sources
  - [ ] Article deduplication (by URL)
  - [ ] Article categorization (stock/sector/macro/government/international)
  - [ ] Sentiment analysis using DeepSeek R1 7B
  - [ ] Macro news categorization and sector impact mapping
  - [ ] Macro-to-stock sentiment propagation
  - [ ] Daily sentiment aggregation (stock-specific + sector + macro)
  - [ ] Database storage (news_articles, sentiment_scores, macro_stock_sentiment)
- [ ] News fetcher module (`data_sources/news_fetcher.py`)
  - [ ] RSS feed parser (Economic Times, Moneycontrol, Business Standard)
  - [ ] NSE/BSE announcement fetcher
  - [ ] Article content extraction
  - [ ] Source configuration management
- [ ] Sentiment repository (`database/repositories/sentiment_repo.py`)
  - [ ] Article storage and retrieval
  - [ ] Sentiment score storage
  - [ ] Macro sentiment mapping storage
  - [ ] Daily aggregation queries
- [ ] News Sentiment Analyst tests
- [ ] Integration with Strategy Specialist (sentiment input)

### 3.6 Agent #6: Portfolio Guardian
- [ ] Portfolio Guardian agent (`agents/portfolio_guardian.py`)
  - [ ] Portfolio monitoring loop (5-minute intervals)
  - [ ] Position tracking
  - [ ] Stop loss monitoring
  - [ ] Target monitoring
  - [ ] Portfolio heat calculation
  - [ ] Risk assessment
  - [ ] Alert generation
  - [ ] Emergency stop logic
- [ ] Portfolio Guardian tests
- [ ] Integration with CrewAI (or standalone cron)

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

## Phase 5: Orchestration

### 5.1 Main Orchestrator
- [ ] Main orchestrator (`main.py`)
  - [ ] Agent initialization
  - [ ] CrewAI setup and configuration
  - [ ] Workflow definition
  - [ ] Agent coordination
  - [ ] Error handling
  - [ ] Graceful shutdown
- [ ] Orchestrator configuration
- [ ] Workflow state management

### 5.2 CrewAI Setup
- [ ] CrewAI crew configuration
  - [ ] Agent definitions
  - [ ] Task definitions
  - [ ] Workflow orchestration
  - [ ] LLM configuration per agent
- [ ] CrewAI tools setup
  - [ ] Database query tool
  - [ ] Data fetching tool
  - [ ] Signal generation tool
  - [ ] Order placement tool

### 5.3 Workflow Management
- [ ] Signal generation workflow
  - [ ] User query → Librarian → Scraper → Strategy
  - [ ] Signal storage
  - [ ] Approval request
- [ ] Trade execution workflow
  - [ ] Approval → Order → Execution → Logging
- [ ] Monitoring workflow
  - [ ] Guardian monitoring loop
  - [ ] Alert generation

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
- **Documentation Complete (v1.1.0)**:
  - Merged 3 news documentation files into comprehensive guide
  - Updated all NSE references to BSE
  - Removed 7 redundant documentation files
  - Added Git workflow guide
  - Updated documentation index
  - Enhanced troubleshooting guides

### In Progress 🚧
- None currently

### Pending ⏳
- Phase 2.1: Shoonya API Integration (Primary)
- Phase 2.2: Upstox API Integration (Backup)
- Phase 3: Agent Implementation (including News Sentiment Analyst)
  - Base agent framework
  - All 5 agents (Database Librarian, Data Scraper, Strategy Specialist, Telegram Assistant, News Sentiment Analyst)
  - Portfolio Guardian (Agent #6)
- Phase 4-10: All remaining phases

---

## 🎯 Priority Order Summary

1. **Foundation** (Phase 1) - Complete infrastructure
2. **Data Sources** (Phase 2) - Enable data collection
3. **Agents** (Phase 3) - Core functionality
4. **Services** (Phase 4) - Business logic
5. **Orchestration** (Phase 5) - System coordination
6. **UI** (Phase 6) - User interaction
7. **Resilience** (Phase 7) - Safety mechanisms
8. **Testing** (Phase 8) - Quality assurance
9. **Deployment** (Phase 9) - Production setup
10. **Production** (Phase 10) - Final polish

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
