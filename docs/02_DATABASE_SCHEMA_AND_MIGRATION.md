# Database Schema & Migration Guide

**Version**: 1.1  
**Last Updated**: January 2025  
**Database**: SQLite 3.x  
**Status**: Updated with Sentiment Analysis Tables

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Schema](#complete-schema)
3. [Table Descriptions](#table-descriptions)
4. [Relationships](#relationships)
5. [Indexes](#indexes)
6. [Data Retention](#data-retention)
7. [Migration Guide](#migration-guide)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Optimization](#performance-optimization)
10. [Common Queries](#common-queries)

---

## Overview

### Database Specifications

- **Type**: SQLite 3.x
- **Location**: `data/trading.db`
- **Size**: ~2GB (1.2M rows expected)
- **Encoding**: UTF-8
- **Backup**: Daily automated backups

### Key Statistics

- **Stocks**: ~500 (Nifty 500)
- **Daily Data**: 2 years × 500 stocks × ~250 trading days = ~250,000 rows
- **Intraday Data**: 60 days × 500 stocks × 6 hours = ~180,000 rows
- **News Articles**: 500 stocks × 5 articles/day × 30 days = ~75,000 rows (30-day retention)
- **Sentiment Scores**: 500 stocks × 365 days = ~182,500 rows (permanent)
- **Total Expected**: ~1.5M rows (including sentiment data)

### Design Principles

1. **Normalization**: 3NF where possible
2. **Indexing**: Strategic indexes for query performance
3. **Audit Trail**: Complete history of all actions
4. **Data Integrity**: Foreign keys and constraints
5. **Performance**: Optimized for read-heavy workloads

---

## Complete Schema

### DDL (Data Definition Language)

```sql
-- ============================================
-- STOCK MASTER TABLE
-- ============================================
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL DEFAULT 'NSE',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_stocks_exchange ON stocks(exchange);
CREATE INDEX idx_stocks_active ON stocks(is_active);

-- ============================================
-- DAILY MARKET DATA (2 years history)
-- ============================================
CREATE TABLE market_data_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date DATE NOT NULL,
    
    -- OHLCV
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    
    -- MOMENTUM INDICATORS
    rsi REAL,
    stoch_k REAL,
    stoch_d REAL,
    williams_r REAL,
    
    -- TREND INDICATORS
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    adx REAL,
    adx_positive REAL,
    adx_negative REAL,
    atr REAL,
    
    -- VOLATILITY INDICATORS
    bollinger_upper REAL,
    bollinger_lower REAL,
    bollinger_middle REAL,
    cci REAL,
    
    -- VOLUME INDICATORS
    obv REAL,
    mfi REAL,
    volume_sma REAL,
    volume_ratio REAL,
    
    -- MOVING AVERAGES
    sma_20 REAL,
    sma_50 REAL,
    sma_200 REAL,
    ema_12 REAL,
    ema_26 REAL,
    ema_20 REAL,
    ema_50 REAL,
    
    -- PRICE ACTION
    price_change REAL,
    price_change_percent REAL,
    high_low_range REAL,
    high_low_range_percent REAL,
    momentum REAL,
    roc REAL,
    
    -- METADATA
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);

CREATE INDEX idx_daily_stock_date ON market_data_daily(stock_id, date);
CREATE INDEX idx_daily_date ON market_data_daily(date);
CREATE INDEX idx_daily_rsi ON market_data_daily(rsi);
CREATE INDEX idx_daily_macd ON market_data_daily(macd);

-- ============================================
-- INTRADAY MARKET DATA (60 days, 1h bars)
-- ============================================
CREATE TABLE market_data_intraday (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    interval TEXT NOT NULL DEFAULT '1h',
    
    -- OHLCV
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, timestamp, interval)
);

CREATE INDEX idx_intraday_stock_timestamp ON market_data_intraday(stock_id, timestamp);
CREATE INDEX idx_intraday_timestamp ON market_data_intraday(timestamp);

-- ============================================
-- SCREENING SIGNALS
-- ============================================
CREATE TABLE screening_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    signal_type TEXT NOT NULL,  -- 'BUY', 'SELL', 'HOLD'
    confidence_score REAL NOT NULL,  -- 0-100
    entry_price REAL,
    stop_loss REAL,
    target_price REAL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_signals_stock ON screening_signals(stock_id);
CREATE INDEX idx_signals_type ON screening_signals(signal_type);
CREATE INDEX idx_signals_confidence ON screening_signals(confidence_score);
CREATE INDEX idx_signals_created ON screening_signals(created_at);

-- ============================================
-- AGENT DECISIONS (Audit Trail)
-- ============================================
CREATE TABLE agent_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,  -- 'strategy_specialist', 'database_librarian', etc.
    stock_id INTEGER,
    decision_type TEXT NOT NULL,  -- 'BUY_RECOMMENDATION', 'SQL_QUERY', etc.
    reasoning TEXT,
    confidence_score REAL,
    input_data TEXT,  -- JSON string
    output_data TEXT,  -- JSON string
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_decisions_agent ON agent_decisions(agent_name);
CREATE INDEX idx_decisions_stock ON agent_decisions(stock_id);
CREATE INDEX idx_decisions_type ON agent_decisions(decision_type);
CREATE INDEX idx_decisions_created ON agent_decisions(created_at);

-- ============================================
-- ORDERS (Approval Workflow)
-- ============================================
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    order_type TEXT NOT NULL,  -- 'BUY', 'SELL'
    quantity INTEGER NOT NULL,
    price REAL,  -- Limit price
    order_status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',  -- 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'EXECUTED', 'FAILED', 'CANCELLED'
    
    -- Trade plan details
    entry_price REAL,
    stop_loss REAL,
    target_price REAL,
    confidence_score REAL,
    
    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    rejected_at DATETIME,
    executed_at DATETIME,
    
    -- Execution details
    executed_price REAL,
    execution_message TEXT,
    broker_order_id TEXT,  -- Shoonya/Upstox order ID
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_orders_stock ON orders(stock_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_created ON orders(created_at);

-- ============================================
-- TRADES (Executed Trades)
-- ============================================
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    stock_id INTEGER NOT NULL,
    buy_sell TEXT NOT NULL,  -- 'BUY', 'SELL'
    quantity INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    stop_loss REAL,
    target REAL,
    pnl REAL DEFAULT 0.0,
    pnl_percent REAL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'OPEN',  -- 'OPEN', 'CLOSED', 'STOP_LOSS_HIT', 'TARGET_HIT'
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    executed_at DATETIME,
    closed_at DATETIME,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE INDEX idx_trades_stock ON trades(stock_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_order ON trades(order_id);
CREATE INDEX idx_trades_created ON trades(created_at);

-- ============================================
-- PORTFOLIO (Current Holdings)
-- ============================================
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    avg_price REAL NOT NULL,
    current_price REAL NOT NULL,
    unrealized_pnl REAL DEFAULT 0.0,
    realized_pnl REAL DEFAULT 0.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_portfolio_stock ON portfolio(stock_id);

-- ============================================
-- USER ACTIONS (Audit Trail)
-- ============================================
CREATE TABLE user_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,  -- 'APPROVE_ORDER', 'REJECT_ORDER', 'KILL_ALL', etc.
    details TEXT,  -- JSON string
    user_id TEXT,  -- Telegram user ID
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_type ON user_actions(action_type);
CREATE INDEX idx_actions_user ON user_actions(user_id);
CREATE INDEX idx_actions_timestamp ON user_actions(timestamp);

-- ============================================
-- PERFORMANCE METRICS
-- ============================================
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,  -- 'total_pnl', 'win_rate', 'profit_factor', etc.
    value REAL NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metric_metadata TEXT  -- JSON string
);

CREATE INDEX idx_metrics_name ON performance_metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON performance_metrics(timestamp);

-- ============================================
-- TAX LEDGER (Compliance)
-- ============================================
CREATE TABLE tax_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    tax_type TEXT NOT NULL,  -- 'STCG', 'LTCG', 'STT', etc.
    amount REAL NOT NULL,
    financial_year TEXT NOT NULL,  -- '2024-25'
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trade_id) REFERENCES trades(id)
);

CREATE INDEX idx_tax_trade ON tax_ledger(trade_id);
CREATE INDEX idx_tax_fy ON tax_ledger(financial_year);
CREATE INDEX idx_tax_type ON tax_ledger(tax_type);

-- ============================================
-- NIFTY 500 SECTORS (Reference Data)
-- ============================================
CREATE TABLE nifty500_sectors (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT,
    industry TEXT,
    market_cap_rank INTEGER
);

CREATE INDEX idx_sectors_sector ON nifty500_sectors(sector);
CREATE INDEX idx_sectors_industry ON nifty500_sectors(industry);

-- ============================================
-- NEWS ARTICLES (30 days retention)
-- ============================================
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER,  -- NULL for macro/news
    source TEXT NOT NULL,  -- 'economic_times', 'moneycontrol', etc.
    title TEXT NOT NULL,
    content TEXT NOT NULL,  -- Full article text
    url TEXT UNIQUE NOT NULL,
    published_date DATETIME NOT NULL,
    category TEXT,  -- 'stock_specific', 'sector', 'macro', 'government', 'international'
    relevance_score REAL,  -- 0-1 (how relevant to trading)
    is_macro BOOLEAN DEFAULT 0,
    macro_category TEXT,  -- 'rbi_rate_cut', 'gdp_growth', etc.
    affected_sectors TEXT,  -- JSON array
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_news_stock ON news_articles(stock_id);
CREATE INDEX idx_news_date ON news_articles(published_date);
CREATE INDEX idx_news_category ON news_articles(category);
CREATE INDEX idx_news_relevance ON news_articles(relevance_score);
CREATE INDEX idx_news_macro ON news_articles(is_macro, macro_category);

-- Full-text search index (SQLite FTS5)
CREATE VIRTUAL TABLE news_articles_fts USING fts5(
    title, content, content=news_articles, content_rowid=id
);

-- ============================================
-- SENTIMENT SCORES (Daily aggregated)
-- ============================================
CREATE TABLE sentiment_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER,  -- NULL for market-wide sentiment
    date DATE NOT NULL,
    
    -- Sentiment metrics
    overall_sentiment REAL NOT NULL,  -- -1 (bearish) to +1 (bullish)
    confidence REAL NOT NULL,  -- 0-1 (how confident in sentiment)
    article_count INTEGER DEFAULT 0,  -- Number of articles analyzed
    
    -- Sentiment breakdown
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    
    -- Category-specific sentiment
    stock_specific_sentiment REAL,  -- News about this stock
    sector_sentiment REAL,  -- News about sector
    macro_sentiment REAL,  -- Macro economic news
    government_sentiment REAL,  -- Government policy news
    international_sentiment REAL,  -- International trade news
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
);

CREATE INDEX idx_sentiment_stock_date ON sentiment_scores(stock_id, date);
CREATE INDEX idx_sentiment_date ON sentiment_scores(date);
CREATE INDEX idx_sentiment_overall ON sentiment_scores(overall_sentiment);

-- ============================================
-- MACRO-TO-STOCK SENTIMENT MAPPING
-- ============================================
CREATE TABLE macro_stock_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_article_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    macro_sentiment REAL NOT NULL,  -- Original macro sentiment
    sector_impact REAL NOT NULL,     -- Sector-level impact
    stock_sentiment REAL NOT NULL,   -- Final stock-specific sentiment
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (news_article_id) REFERENCES news_articles(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE INDEX idx_macro_stock ON macro_stock_sentiment(stock_id, created_at);
CREATE INDEX idx_macro_news ON macro_stock_sentiment(news_article_id);

-- ============================================
-- NEWS SOURCES (Configuration)
-- ============================================
CREATE TABLE news_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- 'economic_times', 'moneycontrol'
    url_pattern TEXT NOT NULL,  -- RSS/API endpoint
    api_key TEXT,  -- If required
    is_active BOOLEAN DEFAULT 1,
    fetch_frequency INTEGER DEFAULT 15,  -- minutes
    last_fetched DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table Descriptions

### 1. `stocks`

**Purpose**: Master list of all tradable stocks

**Key Fields**:
- `symbol`: Unique identifier (e.g., "NSE|TCS-EQ")
- `name`: Company name
- `exchange`: Exchange code (NSE, BSE)
- `is_active`: Whether stock is currently tradable

**Usage**: Reference table for all other tables

---

### 2. `market_data_daily`

**Purpose**: Daily OHLCV + 29 technical indicators (2 years history)

**Key Fields**:
- `stock_id`: Foreign key to stocks
- `date`: Trading date
- `open, high, low, close, volume`: OHLCV data
- `rsi, macd, bollinger_*`: Technical indicators
- **29 Indicators Total**: See schema above

**Data Volume**: ~250,000 rows (500 stocks × 250 days × 2 years)

**Retention**: 2 years (older data archived)

---

### 3. `market_data_intraday`

**Purpose**: Intraday data (60 days, 1h bars)

**Key Fields**:
- `stock_id`: Foreign key to stocks
- `timestamp`: Bar timestamp
- `interval`: Time interval (default "1h")
- `open, high, low, close, volume`: OHLCV data

**Data Volume**: ~180,000 rows (500 stocks × 6 hours × 60 days)

**Retention**: 60 days (older data deleted)

---

### 4. `screening_signals`

**Purpose**: Agent-generated trading signals

**Key Fields**:
- `stock_id`: Foreign key to stocks
- `signal_type`: BUY, SELL, or HOLD
- `confidence_score`: 0-100
- `entry_price, stop_loss, target_price`: Trade plan

**Usage**: Signals generated by Strategy Specialist

---

### 5. `agent_decisions`

**Purpose**: Complete audit trail of all agent decisions

**Key Fields**:
- `agent_name`: Which agent made the decision
- `decision_type`: Type of decision
- `reasoning`: Agent's reasoning (text)
- `input_data, output_data`: JSON strings

**Usage**: Debugging, compliance, analysis

---

### 6. `orders`

**Purpose**: Order workflow with approval

**Key Fields**:
- `order_status`: PENDING_APPROVAL → APPROVED → EXECUTED
- `broker_order_id`: External broker order ID
- `entry_price, stop_loss, target_price`: Trade plan

**Workflow**: 
1. Created (PENDING_APPROVAL)
2. User approves/rejects
3. If approved, executed
4. Status updated

---

### 7. `trades`

**Purpose**: All executed trades

**Key Fields**:
- `entry_price, exit_price`: Trade prices
- `pnl, pnl_percent`: Profit/loss
- `status`: OPEN, CLOSED, STOP_LOSS_HIT, TARGET_HIT

**Usage**: Performance tracking, tax reporting

---

### 8. `portfolio`

**Purpose**: Current portfolio holdings

**Key Fields**:
- `quantity`: Number of shares
- `avg_price`: Average purchase price
- `current_price`: Current market price
- `unrealized_pnl`: Current profit/loss

**Usage**: Real-time portfolio monitoring

---

### 9. `user_actions`

**Purpose**: Audit trail of user actions

**Key Fields**:
- `action_type`: Type of action
- `details`: JSON with action details
- `user_id`: Telegram user ID

**Usage**: Compliance, debugging

---

### 10. `performance_metrics`

**Purpose**: Performance tracking metrics

**Key Fields**:
- `metric_name`: Metric name (win_rate, profit_factor, etc.)
- `value`: Metric value
- `timestamp`: When calculated

**Usage**: Performance analysis, reporting

---

### 11. `tax_ledger`

**Purpose**: Tax compliance tracking

**Key Fields**:
- `trade_id`: Foreign key to trades
- `tax_type`: STCG, LTCG, STT, etc.
- `amount`: Tax amount
- `financial_year`: FY (e.g., "2024-25")

**Usage**: Tax reporting, compliance

---

### 12. `nifty500_sectors`

**Purpose**: Reference data for Nifty 500 stocks

**Key Fields**:
- `symbol`: Stock symbol
- `sector, industry`: Classification
- `market_cap_rank`: Market cap ranking

**Usage**: Sector-based screening, analysis

---

### 13. `news_articles`

**Purpose**: Store all fetched news articles (30-day retention)

**Key Fields**:
- `stock_id`: Foreign key to stocks (NULL for macro/news)
- `source`: News source (economic_times, moneycontrol, etc.)
- `title, content`: Article text
- `url`: Unique article URL
- `published_date`: When article was published
- `category`: stock_specific, sector, macro, government, international
- `is_macro`: Whether this is macro-level news
- `macro_category`: Specific macro event (rbi_rate_cut, gdp_growth, etc.)
- `affected_sectors`: JSON array of affected sectors

**Data Volume**: ~75,000 rows (500 stocks × 5 articles/day × 30 days)

**Retention**: 30 days (older articles archived)

**Usage**: News storage, sentiment analysis, full-text search

---

### 14. `sentiment_scores`

**Purpose**: Daily aggregated sentiment scores per stock

**Key Fields**:
- `stock_id`: Foreign key to stocks (NULL for market-wide)
- `date`: Trading date
- `overall_sentiment`: -1.0 (bearish) to +1.0 (bullish)
- `confidence`: 0.0 to 1.0 (how confident in sentiment)
- `article_count`: Number of articles analyzed
- `stock_specific_sentiment`: Direct news about stock
- `sector_sentiment`: Sector-wide news
- `macro_sentiment`: Macro news propagated to stock

**Data Volume**: ~182,500 rows (500 stocks × 365 days)

**Retention**: Permanent (daily aggregated)

**Usage**: Feed to Strategy Specialist for enhanced trade signals

---

### 15. `macro_stock_sentiment`

**Purpose**: Mapping of macro news to individual stock sentiment

**Key Fields**:
- `news_article_id`: Foreign key to news_articles
- `stock_id`: Foreign key to stocks
- `macro_sentiment`: Original macro sentiment
- `sector_impact`: Sector-level impact multiplier
- `stock_sentiment`: Final stock-specific sentiment

**Data Volume**: ~50,000 rows (estimated)

**Retention**: 90 days (detailed mapping)

**Usage**: Track how macro events affect individual stocks

---

### 16. `news_sources`

**Purpose**: Configuration for news sources

**Key Fields**:
- `name`: Source name (economic_times, moneycontrol, etc.)
- `url_pattern`: RSS/API endpoint
- `api_key`: API key if required
- `is_active`: Whether source is active
- `fetch_frequency`: Fetch interval in minutes
- `last_fetched`: Last fetch timestamp

**Usage**: News source configuration and monitoring

---

## Relationships

### Entity Relationship Diagram

```
stocks (1) ──< (many) market_data_daily
stocks (1) ──< (many) market_data_intraday
stocks (1) ──< (many) screening_signals
stocks (1) ──< (many) agent_decisions
stocks (1) ──< (many) orders
stocks (1) ──< (many) trades
stocks (1) ──< (1) portfolio
stocks (1) ──< (many) news_articles
stocks (1) ──< (many) sentiment_scores

orders (1) ──< (many) trades
trades (1) ──< (many) tax_ledger
news_articles (1) ──< (many) macro_stock_sentiment
```

### Foreign Key Constraints

All foreign keys are enforced:
- `market_data_daily.stock_id` → `stocks.id`
- `market_data_intraday.stock_id` → `stocks.id`
- `screening_signals.stock_id` → `stocks.id`
- `agent_decisions.stock_id` → `stocks.id`
- `orders.stock_id` → `stocks.id`
- `trades.stock_id` → `stocks.id`
- `trades.order_id` → `orders.id`
- `portfolio.stock_id` → `stocks.id`
- `tax_ledger.trade_id` → `trades.id`
- `news_articles.stock_id` → `stocks.id`
- `sentiment_scores.stock_id` → `stocks.id`
- `macro_stock_sentiment.news_article_id` → `news_articles.id`
- `macro_stock_sentiment.stock_id` → `stocks.id`

---

## Indexes

### Performance Indexes

**Primary Indexes**:
- All tables have `id` as PRIMARY KEY
- Foreign keys are indexed

**Composite Indexes**:
- `market_data_daily(stock_id, date)`: For stock history queries
- `market_data_intraday(stock_id, timestamp)`: For intraday queries
- `orders(stock_id, order_status)`: For order lookups
- `trades(stock_id, status)`: For trade queries

**Single Column Indexes**:
- `market_data_daily(date)`: For date-based queries
- `market_data_daily(rsi)`: For RSI screening
- `screening_signals(confidence_score)`: For signal filtering
- `agent_decisions(created_at)`: For audit queries

### Index Maintenance

- Indexes are created automatically with schema
- No manual maintenance required for SQLite
- VACUUM periodically to optimize

---

## Data Retention

### Retention Policies

| Table | Retention Period | Action |
|-------|-----------------|--------|
| `market_data_daily` | 2 years | Archive older data |
| `market_data_intraday` | 60 days | Delete older data |
| `news_articles` | 30 days | Archive older articles |
| `sentiment_scores` | Permanent | Keep all (daily aggregated) |
| `macro_stock_sentiment` | 90 days | Archive older mappings |
| `trades` | Permanent | Keep all |
| `orders` | 1 year | Archive older |
| `agent_decisions` | 1 year | Archive older |
| `user_actions` | 1 year | Archive older |
| `performance_metrics` | Permanent | Keep all |
| `tax_ledger` | Permanent | Keep all |

### Cleanup Script

```python
# scripts/cleanup_old_data.py
from datetime import datetime, timedelta
from database.session import get_session
from database.models import MarketDataDaily, MarketDataIntraday

def cleanup_old_data():
    """Clean up old data based on retention policies."""
    session = get_session()
    
    # Clean intraday data older than 60 days
    cutoff = datetime.now() - timedelta(days=60)
    session.query(MarketDataIntraday).filter(
        MarketDataIntraday.timestamp < cutoff
    ).delete()
    
    # Archive daily data older than 2 years (optional)
    # Move to archive table or file
    
    session.commit()
```

---

## Migration Guide

### Initial Setup

1. **Create Database**:
```bash
python scripts/init_db.py
```

2. **Verify Schema**:
```python
from database.session import init_db
init_db()  # Creates all tables
```

### Schema Changes

**Version 1.0 → 1.1** (Example):
```sql
-- Add new column
ALTER TABLE trades ADD COLUMN notes TEXT;

-- Create new index
CREATE INDEX idx_trades_notes ON trades(notes);
```

**Migration Script**:
```python
# scripts/migrate_v1_0_to_v1_1.py
import sqlite3

def migrate():
    conn = sqlite3.connect('data/trading.db')
    cursor = conn.cursor()
    
    # Add new column
    cursor.execute("ALTER TABLE trades ADD COLUMN notes TEXT")
    
    # Create index
    cursor.execute("CREATE INDEX idx_trades_notes ON trades(notes)")
    
    conn.commit()
    conn.close()
```

### Data Migration

**Backfill Historical Data**:
```python
# scripts/backfill_nifty500.py
from database.repositories.market_data_repo import MarketDataRepository
from data_sources.yfinance_scraper import YFinanceScraper

def backfill_historical_data():
    """Backfill 2 years of historical data."""
    scraper = YFinanceScraper()
    repo = MarketDataRepository(get_session())
    
    symbols = get_nifty500_symbols()
    
    for symbol in symbols:
        data = scraper.get_historical_data(symbol, years=2)
        for row in data:
            repo.add_daily_data(
                stock_id=row['stock_id'],
                date=row['date'],
                **row['ohlcv'],
                **row['indicators']
            )
```

---

## Backup & Recovery

### Backup Strategy

**Daily Backups**:
```python
# scripts/backup_database.py
import shutil
from datetime import datetime

def backup_database():
    """Create daily backup of database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/trading_{timestamp}.db"
    
    shutil.copy2("data/trading.db", backup_path)
    print(f"Backup created: {backup_path}")
```

**Automated Backup** (Windows Task Scheduler):
```powershell
# Run daily at 4:00 AM
python scripts/backup_database.py
```

### Recovery

**Restore from Backup**:
```python
import shutil

def restore_database(backup_path):
    """Restore database from backup."""
    shutil.copy2(backup_path, "data/trading.db")
    print("Database restored")
```

### Backup Retention

- **Daily backups**: Keep 7 days
- **Weekly backups**: Keep 4 weeks
- **Monthly backups**: Keep 12 months

---

## Performance Optimization

### Query Optimization

1. **Use Indexes**: Always query on indexed columns
2. **Limit Results**: Use LIMIT for large result sets
3. **Avoid SELECT ***: Select only needed columns
4. **Use JOINs**: Instead of multiple queries

**Example Optimized Query**:
```sql
-- Good: Uses index, limits results
SELECT symbol, close, rsi 
FROM market_data_daily d
JOIN stocks s ON d.stock_id = s.id
WHERE d.date = (SELECT MAX(date) FROM market_data_daily)
AND d.rsi < 30
ORDER BY d.rsi
LIMIT 15;

-- Bad: Full table scan, no limit
SELECT * FROM market_data_daily WHERE rsi < 30;
```

### Database Maintenance

**VACUUM** (Periodic):
```sql
VACUUM;
```

**ANALYZE** (Update Statistics):
```sql
ANALYZE;
```

**Maintenance Script**:
```python
# scripts/maintain_database.py
import sqlite3

def maintain_database():
    """Run database maintenance."""
    conn = sqlite3.connect('data/trading.db')
    cursor = conn.cursor()
    
    # Vacuum
    cursor.execute("VACUUM")
    
    # Analyze
    cursor.execute("ANALYZE")
    
    conn.close()
```

---

## Common Queries

### Screening Queries

**Oversold RSI Stocks**:
```sql
SELECT s.symbol, d.close, d.rsi
FROM market_data_daily d
JOIN stocks s ON d.stock_id = s.id
WHERE d.date = (SELECT MAX(date) FROM market_data_daily)
AND d.rsi < 30
ORDER BY d.rsi
LIMIT 15;
```

**MACD Crossover**:
```sql
SELECT s.symbol, d.close, d.macd, d.macd_signal
FROM market_data_daily d
JOIN stocks s ON d.stock_id = s.id
WHERE d.date = (SELECT MAX(date) FROM market_data_daily)
AND d.macd > d.macd_signal
AND d.macd > 0
ORDER BY (d.macd - d.macd_signal) DESC
LIMIT 20;
```

**Volume Surge**:
```sql
SELECT s.symbol, d.close, d.volume, d.volume_ratio
FROM market_data_daily d
JOIN stocks s ON d.stock_id = s.id
WHERE d.date = (SELECT MAX(date) FROM market_data_daily)
AND d.volume_ratio > 2.0
ORDER BY d.volume_ratio DESC
LIMIT 20;
```

### Performance Queries

**Win Rate**:
```sql
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades
WHERE status = 'CLOSED';
```

**Profit Factor**:
```sql
SELECT 
    SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) / 
    ABS(SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END)) as profit_factor
FROM trades
WHERE status = 'CLOSED';
```

**Sector Exposure**:
```sql
SELECT 
    sec.sector,
    SUM(p.quantity * p.current_price) as exposure,
    ROUND(100.0 * SUM(p.quantity * p.current_price) / 
          (SELECT SUM(quantity * current_price) FROM portfolio), 2) as exposure_pct
FROM portfolio p
JOIN stocks s ON p.stock_id = s.id
JOIN nifty500_sectors sec ON s.symbol = sec.symbol
GROUP BY sec.sector
ORDER BY exposure DESC;
```

---

## Troubleshooting

### Common Issues

1. **Database Locked**:
   - Ensure only one process accesses database
   - Use connection pooling
   - Check for long-running transactions

2. **Slow Queries**:
   - Check if indexes are used (EXPLAIN QUERY PLAN)
   - Optimize query structure
   - Consider partitioning

3. **Disk Space**:
   - Monitor database size
   - Clean up old data
   - Compress backups

### Diagnostic Queries

**Check Database Size**:
```sql
SELECT 
    page_count * page_size as size_bytes,
    page_count * page_size / 1024 / 1024 as size_mb
FROM pragma_page_count(), pragma_page_size();
```

**Check Table Sizes**:
```sql
SELECT 
    name,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count
FROM sqlite_master m
WHERE type='table';
```

**Check Index Usage**:
```sql
EXPLAIN QUERY PLAN
SELECT * FROM market_data_daily WHERE rsi < 30;
```

---

**Next Documents**:
- `03_AGENT_IMPLEMENTATION.md` - Detailed agent implementation guide
- `04_CONFIGURATION_REFERENCE.md` - Complete configuration reference
