# Architecture & Design Document

**Version**: 1.1  
**Last Updated**: January 2025  
**Status**: Production Ready (Phase 1 & 2 Complete)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Agent Architecture](#agent-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Principles](#design-principles)
7. [Component Details](#component-details)
8. [Integration Points](#integration-points)
9. [Scalability Considerations](#scalability-considerations)

---

## System Overview

### Purpose

A production-ready, agentic AI swing trading system for Nifty 500 stocks with:
- **5-Agent Architecture**: Specialized agents for different functions
- **Human-in-Loop**: Manual approval required for all trades
- **Multi-Source Data**: Shoonya (primary), Upstox (backup), yfinance (historical)
- **News Sentiment Analysis**: Multi-source news aggregation and sentiment analysis
- **Real-time Monitoring**: Portfolio Guardian for risk management
- **Telegram Interface**: Mobile-first user interaction

### Key Features

- **Swing Trading Focus**: 2-6 week holding periods
- **Risk Management**: 2% stop loss, 4% target, 5% max risk per trade
- **29 Technical Indicators**: Comprehensive technical analysis
- **News Sentiment Integration**: Stock-specific, sector, and macro sentiment analysis
- **Audit Trail**: Complete logging of all agent decisions
- **Tax Compliance**: Built-in tax ledger for reporting

### System Constraints

- **RAM**: 8GB minimum (sequential model loading)
- **Storage**: ~2GB for database (1.2M rows)
- **Network**: Stable internet for API calls
- **Market Hours**: 9:15 AM - 3:30 PM IST

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│  ┌──────────────┐              ┌──────────────┐                │
│  │   Telegram   │              │   Streamlit  │                │
│  │    Bot       │              │   Dashboard  │                │
│  └──────┬───────┘              └──────┬───────┘                │
└─────────┼─────────────────────────────┼─────────────────────────┘
          │                             │
          └─────────────┬───────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Main Orchestrator (main.py)                 │  │
│  │  - Agent coordination                                    │  │
│  │  - Workflow management                                   │  │
│  │  - Error handling                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   AGENT #4   │ │  AGENT #1   │ │  AGENT #2   │
│  TELEGRAM    │ │  LIBRARIAN  │ │   SCRAPER   │
│  ASSISTANT   │ │             │ │             │
└───────┬──────┘ └──────┬──────┘ └──────┬──────┘
        │               │               │
        │       ┌───────▼───────┐       │
        │       │   SQLite DB   │       │
        │       │  (1.2M rows)  │       │
        │       └───────┬───────┘       │
        │               │               │
        │       ┌───────▼───────┐       │
        │       │  AGENT #3     │       │
        │       │  STRATEGY     │       │
        │       │  SPECIALIST   │       │
        │       └───────┬───────┘       │
        │               │               │
        │       ┌───────▼───────┐       │
        │       │  AGENT #5     │       │
        │       │  NEWS        │       │
        │       │  SENTIMENT    │       │
        │       └───────┬───────┘       │
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      AGENT #6: GUARDIAN       │
        │   (5-minute monitoring loop)  │
        └───────────────┬───────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                    EXTERNAL SERVICES LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Shoonya    │  │    Upstox    │  │   Ollama     │         │
│  │  WebSocket   │  │   REST API   │  │    Cloud     │         │
│  │  (Primary)   │  │   (Backup)   │  │   (LLM)      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

### Agent #1: Database Librarian

**Purpose**: Natural language to SQL translation

**Model**: `qwen3-coder:480b` (primary), `devstral-2:123b` (fallback)  
**Temperature**: 0.1 (precision critical)

**Responsibilities**:
- Translate user queries to optimized SQL
- Understand database schema
- Generate safe, parameterized queries
- Handle complex joins and aggregations

**Input Format**:
```
"Show me oversold RSI stocks today"
"Find IT sector gainers with MACD crossover"
"List stocks with volume surge above 200%"
```

**Output Format**:
```sql
SELECT symbol, close, rsi_14 
FROM market_data_daily 
WHERE date = (SELECT MAX(date) FROM market_data_daily)
AND rsi_14 < 30 
ORDER BY rsi_14 
LIMIT 15;
```

**Tables Managed**:
- `market_data_daily` (2 years, 29 indicators)
- `market_data_intraday` (60 days, 1h bars)
- `screening_signals`
- `agent_decisions`
- `trades`
- `user_actions`
- `performance_metrics`
- `tax_ledger`

**Error Handling**:
- Invalid queries return "INVALID_QUERY"
- SQL injection protection via parameterization
- Fallback to simpler query on failure

---

### Agent #2: Data Scraper

**Purpose**: Multi-source data collection with resilience

**Model**: None (Python functions only)

**Data Sources** (Priority Order):
1. **Shoonya WebSocket** (Primary)
   - Real-time OHLCV data
   - 500+ stocks simultaneously
   - WebSocket streaming
   
2. **Upstox REST API** (Backup)
   - 1-minute polling fallback
   - Batch requests (50 stocks per request)
   - Used when Shoonya fails
   
3. **yfinance** (Historical)
   - Daily backfill
   - Historical data gaps
   - Free historical data

**Validation Rules**:
- **Price Sanity**: `|current - prev_close| < 10%`
- **Volume Sanity**: `volume > 0.1 * avg_volume_20d`
- **Freshness**: `timestamp > NOW() - 2min`
- **Format**: `{"symbol": "NSE|TCS-EQ", "ltp": 3245.5, "valid": true}`

**NSE Symbol Format**:
- Equity: `NSE|TCS-EQ`
- Index: `NSE|NIFTY50-INDEX`
- Futures: `NSE|NIFTY24JANFUT`

**Rate Limiting**:
- Shoonya: WebSocket (no explicit limits)
- Upstox: 10 req/sec, 200 req/min
- yfinance: 1 req/sec (courtesy)

---

### Agent #3: Strategy Specialist

**Purpose**: Generate high-conviction trade recommendations

**Model**: `deepseek-v3.1:671b` (primary), `gpt-oss:120b` (fallback)  
**Temperature**: 0.3 (reasoning consistency)

**Input Format**:
```json
{
  "symbol": "NSE|TCS-EQ",
  "ohlcv_20d": [...],
  "indicators_29": {
    "rsi": 28.5,
    "macd": 12.3,
    "bb_upper": 3300,
    ...
  },
  "sector_exposure": 0.15,
  "sentiment": {
    "overall_sentiment": 0.65,
    "confidence": 0.82,
    "components": {
      "stock_specific": 0.70,
      "sector": 0.60,
      "macro": 0.58
    }
  }
}
```

**Swing Trading Setups** (Require 2+ confirmations):
1. **Oversold Reversal**
   - RSI < 35
   - MACD bullish crossover
   - Volume > 1.5x average
   
2. **Breakout**
   - Close > Bollinger Upper
   - ADX > 25
   - Volume surge
   
3. **Pullback**
   - Close > VWAP
   - Hammer candle pattern
   - Support bounce
   
4. **Trend Continuation**
   - EMA20 > EMA50
   - Pullback to EMA20
   - Volume confirmation

**Risk Rules**:
- **Stop Loss**: 2% max below entry
- **Target**: 4-6% above entry (R:R > 2:1)
- **Position Size**: ₹50k max risk per trade
- **Sector Exposure**: < 20% portfolio
- **Confidence**: > 75% only

**Output Format** (Mandatory JSON):
```json
{
  "action": "BUY",
  "symbol": "NSE|TCS-EQ",
  "entry_price": 3245.5,
  "sl_price": 3180.6,
  "target_price": 3377.2,
  "confidence": 82,
  "reasoning": "RSI 28 + MACD cross + VWAP bounce",
  "risk_reward": 2.1,
  "position_size": 77
}
```

---

### Agent #4: Telegram Assistant

**Purpose**: Human interface for approvals and queries

**Model**: `gemini-3-flash-preview` (primary), `nemotron-3-nano:30b` (fallback)  
**Temperature**: 0.7 (natural conversation)

**Commands**:
- `/start` → Welcome + capabilities
- `/status` → Open positions + P&L
- `/signals` → Latest signals
- `/kill` → Emergency: Close all positions
- `/help` → Command list

**Inline Buttons**:
- ✅ Approve signal
- ❌ Reject signal
- 📊 View details
- 🚫 Cancel order

**Alerts** (Automatic):
- **Heartbeat**: Every 30min "System alive, P&L +1.2%"
- **SL Breach**: "TCS hit SL ₹3180 - AUTO SELL executed"
- **Daily Summary**: "3W/2L, +₹4500, 62% win rate"
- **Emergency**: "API connection lost - Trading paused"

**Workflow Example**:
```
User: "Find me setups"
↓
Bot: "🤖 3 signals ready:
     TCS [✅][❌] ₹3245→3377 (82%) [Sentiment: +0.65]
     INFY [✅][❌] ₹1520→1580 (78%) [Sentiment: +0.58]
     RELIANCE [✅][❌] ₹2450→2550 (75%) [Sentiment: +0.42]"
↓
User clicks TCS ✅
↓
Bot: "Order placed: 77 TCS @ ₹3245
     SL: ₹3180, Target: ₹3377
     Order ID: 12345"
```

---

### Agent #5: News Sentiment Analyst

**Purpose**: News aggregation and sentiment analysis for enhanced trading decisions

**Model**: `deepseek-r1:7b` (primary), `qwen2.5:7b` (fallback)  
**Temperature**: 0.3 (consistent sentiment analysis)

**Data Sources**:
- **Economic Times** (RSS): Markets, economy, policy
- **Moneycontrol** (RSS): Stocks, sectors, market analysis
- **Business Standard** (RSS): Macro, government, economy
- **BSE Announcements**: Corporate actions, results (RSS feed)

**Frequency**: Every 15-30 minutes (market hours)

**Key Functions**:
1. **News Fetching**: RSS feed parsing and article extraction
2. **Article Categorization**: Stock-specific, sector, macro, government, international
3. **Sentiment Analysis**: 
   - DeepSeek R1 7B for complex macro/government news
   - FinBERT (optional) for high-volume simple news
4. **Macro Propagation**: Map macro events to sectors and individual stocks
5. **Daily Aggregation**: Calculate daily sentiment scores per stock

**Sentiment Components**:
- **Stock-Specific**: Direct news about the stock
- **Sector**: Sector-wide news affecting the stock
- **Macro**: Macroeconomic news propagated to the stock (RBI, GDP, etc.)

**Output Format**:
```json
{
  "stock_id": 123,
  "date": "2025-01-15",
  "overall_sentiment": 0.65,
  "confidence": 0.82,
  "components": {
    "stock_specific": 0.70,
    "sector": 0.60,
    "macro": 0.58
  },
  "article_count": 5
}
```

**Integration**: Feeds sentiment data to Strategy Specialist for enhanced trade signals

**Database Tables**:
- `news_articles`: All fetched articles (30-day retention)
- `sentiment_scores`: Daily aggregated sentiment per stock
- `macro_stock_sentiment`: Macro-to-stock sentiment mapping

---

### Agent #5: Portfolio Guardian

**Purpose**: Continuous portfolio monitoring and risk management

**Model**: `deepseek-v3.1:671b` (primary)  
**Temperature**: 0.2  
**Frequency**: Every 5 minutes (APScheduler)

**Input**:
- Shoonya positions
- Live prices (WebSocket)
- News sentiment (optional)
- Earnings calendar (optional)

**Monitoring Rules**:
1. **SL Breach**: `current_price < sl_price` → IMMEDIATE SELL
2. **Near Target**: `current_price > target * 0.95` → "Trail SL?"
3. **Trailing Stop**: `+8% profit` → Move SL to `+5%` lock-in
4. **News Alert**: `sentiment < -0.3` → "Recommend SELL"
5. **Earnings Tomorrow**: Reduce position 50%
6. **Portfolio Heat**: `exposure > 80%` → Block new trades

**Output**:
- Updates `portfolio_monitoring` table
- Sends Telegram alerts
- Executes emergency exits
- Logs all actions

**Actions**:
- `HOLD` - No action needed
- `SELL` - Exit position
- `TRAIL` - Move stop loss
- `WARNING` - Alert user
- `REDUCE` - Partial exit

---

## Data Flow

### Signal Generation Flow

```
1. User Query (Telegram)
   ↓
2. Telegram Assistant routes to Librarian
   ↓
3. Librarian generates SQL query
   ↓
4. Query executed on SQLite DB
   ↓
5. Returns 15 candidate symbols
   ↓
6. Data Scraper fetches live data (Shoonya WebSocket)
   ↓
7. Data validated (price sanity, freshness)
   ↓
8. Strategy Specialist analyzes each symbol
   ↓
9. Generates trade signals (confidence > 75%)
   ↓
10. Telegram Assistant presents signals with buttons
    ↓
11. User approves/rejects
    ↓
12. Approved orders sent to Shoonya API
    ↓
13. Order executed and logged
    ↓
14. Portfolio Guardian starts monitoring
```

### Monitoring Flow (Every 5 Minutes)

```
1. Portfolio Guardian wakes up
   ↓
2. Fetches current positions from Shoonya
   ↓
3. Gets live prices via WebSocket
   ↓
4. Checks each position:
   - SL breach? → SELL
   - Near target? → Alert
   - Trailing stop? → Update SL
   - News sentiment? → Alert
   ↓
5. Updates portfolio_monitoring table
   ↓
6. Sends Telegram alerts if needed
   ↓
7. Sleeps for 5 minutes
```

---

## Technology Stack

### Core Framework
- **CrewAI**: Multi-agent orchestration
- **LangChain**: LLM integration
- **SQLAlchemy**: Database ORM
- **APScheduler**: Task scheduling

### LLM Services
- **Local Ollama**: Model hosting (runs locally)
- **Models** (must be pulled locally):
  - Strategy: `deepseek-r1:7b` (fallback: `qwen2.5:7b`)
  - Librarian: `qwen2.5-coder:7b-instruct` (fallback: `codegemma:7b`)
  - Chatbot: `gemma2:2b-instruct-q4_K_M` (fallback: `phi3:mini`)
  - Guardian: `deepseek-r1:7b`

### Data Sources
- **Shoonya API**: Primary trading & data
- **Upstox API**: Backup data source
- **yfinance**: Historical data

### Database
- **SQLite**: Local database
- **Size**: ~2GB (1.2M rows)
- **Backup**: Daily automated backups

### User Interface
- **Telegram Bot**: `python-telegram-bot`
- **Dashboard**: Streamlit + Plotly

### Technical Analysis
- **pandas-ta**: Technical indicators
- **TA-Lib**: Advanced indicators
- **29 Indicators**: RSI, MACD, Bollinger, etc.

### Utilities
- **loguru**: Logging
- **pydantic**: Configuration validation
- **python-dotenv**: Environment variables

---

## Design Principles

### 1. Separation of Concerns
- Each agent has a single, well-defined responsibility
- No agent depends on another agent's internal implementation
- Clear interfaces between components

### 2. Resilience
- Multi-source data (Shoonya + Upstox + yfinance)
- Fallback models for each agent
- Graceful degradation on failures

### 3. Human-in-Loop
- All trades require manual approval
- Emergency kill switch (`/kill` command)
- Transparent decision-making (agent reasoning logged)

### 4. Auditability
- Complete audit trail in `agent_decisions` table
- All trades logged with reasoning
- User actions tracked

### 5. Risk Management
- Hard limits (2% SL, 4% target)
- Portfolio heat monitoring
- Sector exposure limits
- Daily loss limits

### 6. Performance
- Sequential model loading (RAM constraint)
- Efficient database queries (indexed)
- WebSocket for real-time data
- Caching where appropriate

---

## Component Details

### Main Orchestrator (`main.py`)

**Responsibilities**:
- Initialize all agents
- Coordinate agent interactions
- Handle workflow execution
- Manage error recovery
- Graceful shutdown

**Key Functions**:
```python
async def main():
    # Initialize agents
    librarian = DatabaseLibrarian()
    scraper = DataScraper()
    strategy = StrategySpecialist()
    telegram = TelegramAssistant()
    guardian = PortfolioGuardian()
    
    # Start background tasks
    asyncio.create_task(guardian.monitor_loop())
    asyncio.create_task(telegram.start_polling())
    
    # Main signal generation loop
    while True:
        if is_market_hours():
            # Generate signals
            ...
        await asyncio.sleep(300)  # 5 minutes
```

### Database Layer

**Schema**: See `02_DATABASE_SCHEMA.md`

**Key Tables**:
- `stocks`: Master stock list
- `market_data_daily`: 2 years of daily data
- `market_data_intraday`: 60 days of intraday
- `trades`: All executed trades
- `orders`: Order workflow
- `portfolio`: Current holdings
- `agent_decisions`: Audit trail

**Repositories**:
- `MarketDataRepository`: Market data operations
- `TradeRepository`: Trade operations
- `OrderRepository`: Order operations
- `PortfolioRepository`: Portfolio operations
- `AnalysisRepository`: Analysis operations

### Service Layer

**Services**:
- `TradingService`: Order execution
- `AnalysisService`: Signal aggregation
- `ApprovalService`: Approval workflow
- `NotificationService`: Telegram notifications
- `OllamaService`: LLM integration

### Configuration

**Settings** (`config/settings.py`):
- Environment variables via Pydantic
- Type validation
- Default values
- Environment-specific configs

---

## Integration Points

### Shoonya API Integration
- **WebSocket**: Real-time market data
- **REST API**: Order placement, portfolio
- **Authentication**: Session-based with TOTP
- **Rate Limits**: 10 req/sec for quotes, 20 orders/sec

### Upstox API Integration
- **REST API**: Backup data source
- **Authentication**: OAuth 2.0
- **Rate Limits**: 50 req/sec, 500 req/min
- **Fallback**: Used when Shoonya fails

### Local Ollama Integration
- **Server**: Local Ollama server (http://localhost:11434)
- **Models**: Multiple models per agent (pulled locally)
- **Fallback**: Automatic fallback on failure
- **No Rate Limits**: Local execution, no API limits
- **Setup**: Run `ollama serve` and pull required models

### Telegram Bot Integration
- **Library**: `python-telegram-bot`
- **Commands**: Text commands
- **Inline Buttons**: Approval workflow
- **Alerts**: Push notifications

---

## Scalability Considerations

### Current Limitations
- **RAM**: 8GB constraint (sequential model loading)
- **Database**: SQLite (single-writer)
- **API Rate Limits**: Shoonya/Upstox limits
- **Model Loading**: Sequential only

### Future Scalability Options

1. **Database Migration**
   - SQLite → PostgreSQL for multi-writer
   - Partitioning for large datasets
   - Read replicas for queries

2. **Model Optimization**
   - Model quantization
   - GPU acceleration
   - Model caching

3. **API Scaling**
   - Multiple broker accounts
   - Load balancing
   - Request queuing

4. **Agent Scaling**
   - Parallel agent execution
   - Agent pools
   - Distributed agents

### Performance Metrics

**Target Metrics**:
- Signal generation: < 10 seconds end-to-end
- Database queries: < 100ms
- WebSocket latency: < 1 second
- Order execution: < 5 seconds

---

## Security Considerations

### API Keys
- Stored in `.env` file (not in code)
- `.env` in `.gitignore`
- Never commit credentials

### Database
- Local SQLite (no network exposure)
- Regular backups
- Encrypted backups (optional)

### Trading
- Manual approval required
- Position size limits
- Daily loss limits
- Emergency kill switch

### Logging
- Sensitive data redacted
- Audit trail for compliance
- Log rotation

---

## Error Handling Strategy

### Agent Failures
- Fallback models for each agent
- Graceful degradation
- Error logging

### API Failures
- Multi-source data (Shoonya → Upstox → yfinance)
- Retry logic with exponential backoff
- Circuit breaker pattern

### Database Failures
- Connection retry
- Transaction rollback
- Data validation

### Model Failures
- Fallback models
- Error messages to user
- Logging for debugging

---

## Monitoring & Observability

### Logging
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Format**: Structured logging (JSON)
- **Rotation**: Daily log files
- **Retention**: 30 days

### Metrics
- Signal generation rate
- Trade execution rate
- API response times
- Error rates
- P&L tracking

### Alerts
- Telegram notifications
- Error alerts
- Performance degradation
- Risk limit breaches

---

## Deployment Architecture

### Development
- Local Python environment
- SQLite database
- Local Ollama server
- Telegram bot (polling)

### Production
- Same as development
- Automated backups
- Monitoring dashboard
- Error alerting

### Future Production
- Docker containers
- Cloud deployment
- Database replication
- Load balancing

---

**Next Documents**:
- `02_DATABASE_SCHEMA.md` - Complete database schema
- `03_AGENT_IMPLEMENTATION.md` - Detailed agent implementation
- `04_CONFIGURATION_REFERENCE.md` - Configuration guide
