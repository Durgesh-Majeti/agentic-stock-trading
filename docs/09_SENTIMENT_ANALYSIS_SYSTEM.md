# Sentiment Analysis System

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Design Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [News Sentiment Analyst Agent](#news-sentiment-analyst-agent)
4. [Data Sources](#data-sources)
5. [Sentiment Analysis Methods](#sentiment-analysis-methods)
6. [Macro News Propagation](#macro-news-propagation)
7. [Database Schema](#database-schema)
8. [Integration with Strategy Specialist](#integration-with-strategy-specialist)
9. [Implementation Guide](#implementation-guide)
10. [Performance & Optimization](#performance--optimization)

---

## Overview

### Purpose

The Sentiment Analysis System enhances the trading strategy by incorporating news sentiment into decision-making. It:

- **Aggregates news** from multiple sources (stocks, sectors, macro, government, international)
- **Analyzes sentiment** using LLM-based analysis (DeepSeek R1 7B) and optionally FinBERT
- **Propagates macro news** to individual stocks via sector impact mapping
- **Feeds sentiment data** to Strategy Specialist for enhanced trade signals

### Key Features

- **Multi-source news aggregation**: Economic Times, Moneycontrol, Business Standard, BSE announcements
- **Hybrid sentiment analysis**: DeepSeek R1 7B for complex news, FinBERT for high-volume simple news
- **Macro-to-stock propagation**: Sector impact matrix maps macro events to stock-specific sentiment
- **Daily sentiment aggregation**: Combines stock-specific, sector, and macro sentiment
- **30-day article retention**: Efficient storage with automatic archiving

### Benefits

- **+5-10% confidence score improvement**: Better trade signal quality
- **-10-15% false signal reduction**: News context filters bad technical signals
- **Early warning system**: Negative news can prevent bad trades
- **Macro awareness**: Understands broader market context

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│         News Sources (RSS/API/Scraping)                  │
│  Economic Times | Moneycontrol | Business Standard      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│      Agent #5: News Sentiment Analyst                   │
│  - News fetching (every 15-30 min)                      │
│  - Article deduplication                                 │
│  - Sentiment analysis (DeepSeek R1 7B / FinBERT)       │
│  - Macro categorization                                  │
│  - Sector impact mapping                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Database (SQLite)                           │
│  - news_articles (30 days retention)                     │
│  - sentiment_scores (daily aggregated)                   │
│  - macro_stock_sentiment (propagation mapping)          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│      Agent #3: Strategy Specialist (Enhanced)           │
│  Input: OHLCV + Indicators + SENTIMENT                  │
│  Output: Trade signals with sentiment context           │
└─────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| **News Fetcher** | Fetch articles from RSS/API | `feedparser`, `requests` |
| **Sentiment Analyzer** | Analyze article sentiment | DeepSeek R1 7B, FinBERT (optional) |
| **Macro Categorizer** | Identify macro events | DeepSeek R1 7B |
| **Sector Mapper** | Map macro to sectors | Python dictionary |
| **Stock Propagator** | Calculate stock-specific sentiment | Python logic |
| **Aggregator** | Combine sentiment components | SQL queries |

---

## News Sentiment Analyst Agent

### Role

**Agent #5: News Sentiment Analyst** is responsible for:
- Fetching news articles from configured sources
- Analyzing sentiment using LLM
- Categorizing macro news and mapping to sectors
- Propagating macro sentiment to individual stocks
- Storing articles and sentiment scores in database

### Model Configuration

- **Primary Model**: `deepseek-r1:7b` (same as Strategy Specialist)
- **Fallback Model**: `qwen2.5:7b`
- **Temperature**: 0.3 (consistent sentiment analysis)
- **Context Window**: 128k tokens

### Agent Workflow

```
1. Fetch News (every 15-30 minutes)
   ↓
2. Deduplicate Articles (by URL)
   ↓
3. Categorize Articles
   - Stock-specific
   - Sector
   - Macro
   - Government
   - International
   ↓
4. Analyze Sentiment
   - Simple articles → FinBERT (fast)
   - Complex articles → DeepSeek R1 7B (reasoning)
   ↓
5. Propagate Macro News
   - Identify affected sectors
   - Calculate stock-specific impact
   ↓
6. Store Results
   - Articles → news_articles table
   - Sentiment → sentiment_scores table
   - Macro mapping → macro_stock_sentiment table
```

### Input/Output

**Input**:
- News source configuration
- Stock list (Nifty 500)
- Sector mapping

**Output**:
- Daily sentiment scores per stock
- Article metadata
- Macro event categorization
- Sector impact mapping

---

## Data Sources

### Indian News Sources

#### 1. Economic Times (RSS)
- **URL**: `https://economictimes.indiatimes.com/rssfeeds/`
- **Coverage**: Stocks, macro, government policy
- **Cost**: Free (RSS)
- **Frequency**: Real-time
- **Categories**: Markets, Economy, Policy

#### 2. Moneycontrol (RSS)
- **URL**: `https://www.moneycontrol.com/rss/`
- **Coverage**: Stocks, sectors, market analysis
- **Cost**: Free (RSS)
- **Frequency**: Real-time
- **Categories**: Markets, Stocks, Sectors

#### 3. Business Standard (RSS)
- **URL**: `https://www.business-standard.com/rss/`
- **Coverage**: Macro, government, economy
- **Cost**: Free
- **Frequency**: Real-time
- **Categories**: Economy, Markets, Policy

#### 4. BSE Corporate Announcements
- **URL**: `https://www.bseindia.com/rssxml/Corporate_Announcements.xml`
- **Type**: RSS feed (standard format)
- **Coverage**: Corporate actions, results, announcements
- **Cost**: Free
- **Frequency**: Real-time
- **Categories**: Corporate Actions, Results

### International Sources (Optional)

#### 1. Reuters API (Paid)
- **Coverage**: Global trade, economy
- **Cost**: $100-500/month
- **Frequency**: Real-time

#### 2. Alpha Vantage News API (Free Tier)
- **Coverage**: Global financial news
- **Cost**: Free (limited)
- **Frequency**: Daily

### Source Configuration

```python
NEWS_SOURCES = [
    {
        "name": "economic_times",
        "url": "https://economictimes.indiatimes.com/rssfeeds/",
        "type": "rss",
        "categories": ["markets", "economy", "policy"],
        "fetch_frequency": 15,  # minutes
        "is_active": True
    },
    {
        "name": "moneycontrol",
        "url": "https://www.moneycontrol.com/rss/",
        "type": "rss",
        "categories": ["markets", "stocks"],
        "fetch_frequency": 15,
        "is_active": True
    },
    # ... more sources
]
```

---

## Sentiment Analysis Methods

### Method 1: DeepSeek R1 7B (Primary)

**Why DeepSeek R1 7B**: This model is already integrated into the system for the Strategy Specialist, making it the natural choice for sentiment analysis. It excels at understanding complex financial news and extracting nuanced sentiment that goes beyond simple positive/negative classification.

**Use Cases**:
- Complex macro/government news that requires understanding policy implications
- Articles requiring context understanding (e.g., "rate cut" can be bullish for some sectors, bearish for others)
- Multi-factor sentiment analysis where multiple aspects need to be considered
- Structured data extraction (sentiment scores, confidence, key factors, reasoning)

**Advantages**:
- **Excellent Context Understanding**: 128k token context window allows processing of long articles
- **Reasoning Capabilities**: Can understand that negative news can sometimes be bullish (e.g., rate cuts)
- **Structured JSON Output**: Returns well-formatted sentiment data with confidence scores
- **No Additional Setup**: Already configured and running in the system
- **Market Context Awareness**: Can understand Indian market-specific nuances

**Disadvantages**:
- **Slower Processing**: ~2-5 seconds per article (acceptable for 15-30 min batch processing)
- **Higher Resource Usage**: Requires GPU for optimal performance (but can run on CPU)

**How It Works**: The model receives the article title and content, along with categorization information. It analyzes the text to extract sentiment scores, confidence levels, and key factors. The output is structured JSON that can be directly stored in the database.

**Prompt Template**:

```python
SENTIMENT_PROMPT = """You are a financial sentiment analyst specializing in Indian stock markets.

Analyze the following news article and extract sentiment information.

ARTICLE:
Title: {title}
Content: {content}
Category: {category}
Published: {published_date}

TASK:
1. Determine overall sentiment: -1.0 (very bearish) to +1.0 (very bullish)
2. Assess confidence: 0.0 (uncertain) to 1.0 (very confident)
3. Identify key factors affecting sentiment
4. Determine if this is stock-specific, sector-wide, or macro-level

OUTPUT FORMAT (JSON only):
{{
    "overall_sentiment": 0.65,
    "confidence": 0.82,
    "sentiment_breakdown": {{
        "stock_specific": 0.70,
        "sector": 0.60,
        "macro": 0.55
    }},
    "key_factors": [
        "TCS wins $500M deal",
        "IT sector outlook positive"
    ],
    "reasoning": "Article mentions TCS deal win and positive IT sector outlook. Overall bullish sentiment with high confidence."
}}

IMPORTANT:
- For macro/government news, consider broader market impact
- Negative news can sometimes be bullish (e.g., rate cuts)
- Consider Indian market context and regulations
- Be conservative with confidence scores
"""
```

### Method 2: FinBERT (Optional, Secondary)

**Use Cases**:
- High-volume, simple stock-specific news
- Articles < 2000 characters
- Fast batch processing

**Advantages**:
- Very fast (~10-50ms per article)
- Low resource usage (CPU-friendly)
- Consistent outputs
- Domain-specific training

**Disadvantages**:
- Limited context (512 tokens)
- No reasoning
- May need fine-tuning for Indian markets
- Binary/ternary classification only

**Installation**:

```bash
pip install transformers torch
```

**Usage**:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load FinBERT model
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def finbert_analyze(text: str) -> dict:
    """Analyze sentiment using FinBERT."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Map to sentiment score (-1 to +1)
    sentiment_map = {"positive": 0.5, "negative": -0.5, "neutral": 0.0}
    # ... map predictions to sentiment
    
    return {"overall_sentiment": sentiment_score, "confidence": confidence}
```

### Hybrid Routing Strategy

**Why Hybrid**: Different types of news require different analysis approaches. Simple stock-specific news can be processed quickly with FinBERT, while complex macro news needs the reasoning capabilities of DeepSeek R1 7B.

**Routing Logic**: The system automatically routes articles to the appropriate analyzer based on:
1. **Article Category**: Macro/government news always goes to DeepSeek
2. **Article Length**: Short articles (<2000 chars) can use FinBERT if available
3. **Complexity**: Complex articles requiring context go to DeepSeek

**Benefits**: This approach balances speed and accuracy - fast processing for simple news, deep analysis for complex news. The system can process hundreds of articles efficiently while maintaining high quality sentiment analysis.

**Implementation**: The routing is transparent to the rest of the system - both analyzers return the same format, so downstream components don't need to know which analyzer was used.

```python
def analyze_sentiment(article: dict) -> dict:
    """Route articles to appropriate sentiment analyzer."""
    
    # Simple stock-specific news → FinBERT (fast)
    if (article['category'] == 'stock_specific' and 
        len(article['content']) < 2000 and
        FINBERT_AVAILABLE):
        return finbert_analyze(article)
    
    # Complex macro/government news → DeepSeek (reasoning)
    elif article['category'] in ['macro', 'government', 'international']:
        return deepseek_analyze(article)
    
    # Default: DeepSeek for consistency
    else:
        return deepseek_analyze(article)
```

---

## Macro News Propagation

### Challenge

Macro news (RBI rate cuts, GDP growth, government policy, etc.) affects the entire market, but the impact varies significantly by sector and individual stock. For example:
- An RBI rate cut is **highly positive** for banking and real estate stocks
- The same rate cut has **minimal impact** on IT or pharma stocks
- Within banking, large-cap banks may react differently than small-cap banks

Simply applying the same sentiment score to all stocks would be inaccurate. We need a sophisticated propagation mechanism.

### Solution: Multi-Level Propagation

The system uses a three-level propagation approach that maps macro sentiment to individual stocks:

1. **Level 1: Macro Sentiment**: Extract overall sentiment from the macro news article
2. **Level 2: Sector Impact**: Map the macro event to affected sectors using a predefined impact matrix
3. **Level 3: Stock Weighting**: Apply stock-specific multipliers based on beta and market cap

This ensures that each stock receives a sentiment score that accurately reflects how the macro event affects it specifically.

```
Level 1: Macro News Sentiment
    ↓
Level 2: Sector Impact Mapping
    ↓
Level 3: Stock-Specific Weighting
    ↓
Level 4: Final Stock Sentiment Score
```

### Sector Impact Matrix

```python
MACRO_SECTOR_IMPACT = {
    "rbi_rate_cut": {
        "BANKING": 0.8,      # High positive impact
        "REAL_ESTATE": 0.7,  # High positive impact
        "AUTOMOBILES": 0.6,  # Medium positive
        "IT": 0.2,           # Low impact
        "PHARMA": 0.1,       # Very low impact
    },
    "rbi_rate_hike": {
        "BANKING": 0.6,      # Positive (higher margins)
        "REAL_ESTATE": -0.7, # Negative (higher borrowing costs)
        "AUTOMOBILES": -0.5, # Negative
        "IT": 0.1,           # Neutral
    },
    "gdp_growth_positive": {
        "CEMENT": 0.9,       # High positive
        "STEEL": 0.8,        # High positive
        "BANKING": 0.7,      # Medium positive
        "FMCG": 0.5,         # Medium positive
        "IT": 0.3,           # Low positive
    },
    "crude_oil_price_increase": {
        "OIL_GAS": 0.8,      # High positive
        "AUTOMOBILES": -0.6, # Negative (fuel costs)
        "AVIATION": -0.7,    # Negative
        "PAINTS": -0.5,      # Negative (raw material)
    },
    "government_infrastructure_spending": {
        "CEMENT": 0.9,
        "STEEL": 0.8,
        "ENGINEERING": 0.7,
        "BANKING": 0.6,
    },
    "inflation_high": {
        "FMCG": -0.4,        # Negative (input costs)
        "BANKING": 0.5,      # Positive (rate hikes)
        "REAL_ESTATE": -0.6, # Negative
    }
}
```

### Stock-Specific Weighting

Not all stocks in a sector react equally:

```python
def get_stock_sensitivity(symbol: str) -> float:
    """Get stock-specific sensitivity to macro events."""
    # High beta stocks = more sensitive
    # Large cap stocks = less sensitive (more stable)
    
    stock_data = get_stock_metadata(symbol)
    beta = stock_data.get('beta', 1.0)
    market_cap = stock_data.get('market_cap', 0)
    
    # Beta multiplier (high beta = more sensitive)
    beta_multiplier = min(beta / 1.0, 1.5)  # Cap at 1.5x
    
    # Market cap dampener (large cap = less sensitive)
    if market_cap > 100000:  # > ₹1L cr
        cap_multiplier = 0.8
    elif market_cap > 50000:  # > ₹50K cr
        cap_multiplier = 0.9
    else:
        cap_multiplier = 1.0
    
    return beta_multiplier * cap_multiplier

def calculate_stock_sentiment_from_macro(
    stock_symbol: str,
    macro_sentiment: float,
    macro_category: str,
    stock_sector: str
) -> float:
    """Calculate stock-specific sentiment from macro news."""
    
    # Get sector impact
    sector_impact = MACRO_SECTOR_IMPACT.get(macro_category, {}).get(stock_sector, 0.0)
    
    # Stock-specific multipliers
    stock_multiplier = get_stock_sensitivity(stock_symbol)
    
    # Calculate final sentiment
    stock_sentiment = macro_sentiment * sector_impact * stock_multiplier
    
    return stock_sentiment
```

### Example: RBI Rate Cut → Individual Stock

```
1. Macro News: "RBI cuts repo rate by 25bps"
   → Macro Sentiment: +0.75 (bullish)

2. Sector Impact:
   - BANKING: +0.8 (high positive)
   - REAL_ESTATE: +0.7 (high positive)
   - IT: +0.2 (low impact)

3. Stock: HDFCBANK (Banking sector)
   - Sector impact: 0.8
   - Stock beta: 1.2 (high sensitivity)
   - Market cap: ₹8L cr (large cap, dampener: 0.8)
   - Stock multiplier: 1.2 * 0.8 = 0.96

4. Final Stock Sentiment:
   Stock Sentiment = 0.75 * 0.8 * 0.96 = 0.576 (moderately bullish)

5. Stock: INFY (IT sector)
   - Sector impact: 0.2 (low)
   - Stock multiplier: 0.9
   - Final: 0.75 * 0.2 * 0.9 = 0.135 (slightly positive)
```

### Macro Categorization Prompt

```python
MACRO_CATEGORIZATION_PROMPT = """Analyze this news article and determine:

1. Is this macro-level news? (RBI, government policy, GDP, inflation, etc.)
2. What specific macro event is it? (rate_cut, gdp_growth, infrastructure_spending, etc.)
3. Which sectors are most affected? (list top 3-5 sectors)
4. What is the sentiment? (-1.0 to +1.0)

OUTPUT (JSON):
{{
    "is_macro": true,
    "macro_category": "rbi_rate_cut",
    "affected_sectors": ["BANKING", "REAL_ESTATE", "AUTOMOBILES"],
    "sector_impact": {{
        "BANKING": 0.8,
        "REAL_ESTATE": 0.7,
        "AUTOMOBILES": 0.6
    }},
    "overall_sentiment": 0.75,
    "reasoning": "RBI cuts repo rate by 25bps, positive for rate-sensitive sectors"
}}
"""
```

---

## Database Schema

### New Tables

#### 1. `news_articles`

Stores all fetched news articles (30-day retention).

```sql
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
```

#### 2. `sentiment_scores`

Daily aggregated sentiment scores per stock.

```sql
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
```

#### 3. `macro_stock_sentiment`

Mapping of macro news to individual stock sentiment.

```sql
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
```

#### 4. `news_sources`

Configuration for news sources.

```sql
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

### Data Retention

- **news_articles**: 30 days (archive older)
- **sentiment_scores**: Permanent (daily aggregated)
- **macro_stock_sentiment**: 90 days (detailed mapping)

---

## Integration with Strategy Specialist

### Enhanced Input Format

Strategy Specialist now receives sentiment data:

```json
{
  "symbol": "NSE|HDFCBANK-EQ",
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
      "stock_specific": 0.70,    // Direct news about HDFCBANK
      "sector": 0.60,            // Banking sector news
      "macro": 0.58              // Macro news propagated to HDFCBANK
    },
    "macro_events": [
      {
        "event": "rbi_rate_cut",
        "impact": 0.58,
        "date": "2025-01-15"
      }
    ],
    "recent_news_count": 5,
    "key_headlines": [
      "HDFC Bank reports strong Q3 results",
      "RBI rate cut benefits banking sector"
    ]
  }
}
```

### Enhanced Prompt

Strategy Specialist prompt includes sentiment analysis:

```
You are a 15-year swing trader. Analyze Nifty 500 stocks for 2-6 week holds.

TECHNICAL DATA:
{technical_indicators}

SENTIMENT DATA:
- Overall Sentiment: {sentiment.overall_sentiment} (bullish if >0.3, bearish if <-0.3)
- Stock-Specific: {sentiment.components.stock_specific}
- Sector: {sentiment.components.sector}
- Macro: {sentiment.components.macro}
- Recent News: {sentiment.recent_news_count} articles

TRADING RULES:
- If sentiment is strongly negative (<-0.5), reduce confidence by 20%
- If sentiment is strongly positive (>0.5), increase confidence by 10%
- Never override technical signals with sentiment alone
- Use sentiment as confirmation, not primary signal
- Macro sentiment should never override negative stock-specific news

SWING SETUPS (require 2+ confirmations):
1. Oversold Reversal: RSI < 35 + MACD bullish cross + volume > 1.5x avg + positive sentiment
2. Breakout: Close > BB Upper + ADX > 25 + volume surge + neutral/positive sentiment
...
```

### Sentiment Weight in Decision

```python
def calculate_final_confidence(
    technical_confidence: float,
    sentiment: dict
) -> float:
    """Calculate final confidence with sentiment adjustment."""
    
    base_confidence = technical_confidence
    
    # Sentiment adjustments
    if sentiment['overall_sentiment'] < -0.5:  # Strongly negative
        adjustment = -0.20  # Reduce by 20%
    elif sentiment['overall_sentiment'] < -0.3:  # Negative
        adjustment = -0.10  # Reduce by 10%
    elif sentiment['overall_sentiment'] > 0.5:  # Strongly positive
        adjustment = +0.10  # Increase by 10%
    elif sentiment['overall_sentiment'] > 0.3:  # Positive
        adjustment = +0.05  # Increase by 5%
    else:
        adjustment = 0.0  # Neutral
    
    # Apply adjustment
    final_confidence = base_confidence + adjustment
    
    # Cap at 0-100
    return max(0.0, min(100.0, final_confidence))
```

---

## Implementation Guide

### Phase 1: Foundation (Week 1)

1. **Database Setup**
   ```bash
   python scripts/migrate_add_sentiment_tables.py
   ```

2. **Create News Sentiment Analyst Agent**
   - File: `agents/news_sentiment_analyst.py`
   - Base class: `BaseAgent`
   - Model: DeepSeek R1 7B

3. **Basic RSS Reader**
   - File: `data_sources/news_fetcher.py`
   - Support: Economic Times, Moneycontrol

### Phase 2: Data Collection (Week 2)

1. **News Fetching**
   - Implement RSS feed parsing
   - Article deduplication (by URL)
   - Store in `news_articles` table

2. **Article Categorization**
   - Stock-specific vs. macro detection
   - Sector identification

### Phase 3: Sentiment Analysis (Week 3)

1. **DeepSeek R1 7B Integration**
   - Sentiment analysis prompt
   - JSON output parsing
   - Error handling

2. **Daily Aggregation**
   - Calculate daily sentiment scores
   - Store in `sentiment_scores` table

### Phase 4: Macro Propagation (Week 4)

1. **Sector Impact Matrix**
   - Define macro-to-sector mappings
   - Stock sensitivity calculation

2. **Propagation Logic**
   - Calculate stock-specific sentiment from macro
   - Store in `macro_stock_sentiment` table

### Phase 5: Strategy Integration (Week 5)

1. **Strategy Specialist Enhancement**
   - Add sentiment input
   - Update prompt
   - Confidence adjustment logic

2. **Testing & Optimization**
   - End-to-end testing
   - Performance optimization
   - FinBERT integration (optional)

---

## Performance & Optimization

### Data Fetching

- **Batch Processing**: Fetch all sources in parallel
- **Rate Limiting**: Respect source limits (15-30 min intervals)
- **Deduplication**: Hash-based URL deduplication
- **Caching**: Cache article content for 1 hour

### Sentiment Processing

- **Batch Analysis**: Process 10-20 articles at a time
- **Caching**: Cache sentiment for duplicate articles
- **Async Processing**: Use async/await for I/O operations

### Database Optimization

- **Indexes**: All foreign keys and date columns indexed
- **Partitioning**: Consider partitioning by date for large tables
- **Archiving**: Archive articles older than 30 days
- **VACUUM**: Run VACUUM weekly

### Expected Performance

- **News Fetching**: ~30 seconds for all sources
- **Sentiment Analysis**: ~2-5 seconds per article (DeepSeek)
- **Daily Aggregation**: ~5 minutes for 500 stocks
- **Total Daily Time**: ~15-20 minutes

---

## Success Metrics

### Accuracy Metrics

- **Sentiment Accuracy**: Compare sentiment to 7-day price movement
- **Macro Propagation Accuracy**: Validate sector impact predictions

### Trading Metrics

- **Confidence Improvement**: +5-10% average confidence increase
- **False Signal Reduction**: -10-15% reduction in bad trades
- **Win Rate Improvement**: +2-5% win rate improvement

### Coverage Metrics

- **Article Coverage**: % of stocks with daily sentiment scores
- **Source Coverage**: Number of active news sources
- **Macro Event Detection**: % of macro events correctly categorized

---

## Troubleshooting

### Common Issues

1. **No Articles Fetched**
   - Check RSS feed URLs
   - Verify network connectivity
   - Check source configuration

2. **Sentiment Analysis Fails**
   - Verify Ollama is running
   - Check model availability
   - Review prompt format

3. **Macro Propagation Incorrect**
   - Verify sector mapping
   - Check stock metadata (beta, market cap)
   - Review sector impact matrix

### Debugging

```python
# Check recent articles
SELECT * FROM news_articles 
ORDER BY created_at DESC 
LIMIT 10;

# Check sentiment scores
SELECT s.symbol, ss.overall_sentiment, ss.confidence, ss.date
FROM sentiment_scores ss
JOIN stocks s ON ss.stock_id = s.id
WHERE ss.date = DATE('now')
ORDER BY ss.overall_sentiment DESC;

# Check macro propagation
SELECT s.symbol, mss.macro_sentiment, mss.stock_sentiment
FROM macro_stock_sentiment mss
JOIN stocks s ON mss.stock_id = s.id
WHERE mss.created_at > DATE('now', '-1 day')
LIMIT 20;
```

---

**Next Steps**:
- Review [Agent Implementation Guide](03_AGENT_IMPLEMENTATION_GUIDE.md) for code examples
- Review [Database Schema](02_DATABASE_SCHEMA_AND_MIGRATION.md) for schema details
- Review [Architecture Document](01_ARCHITECTURE_AND_DESIGN.md) for system overview
