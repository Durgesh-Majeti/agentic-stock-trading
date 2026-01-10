# Free Sources for Sentiment Analysis

**Version**: 1.0  
**Last Updated**: January 2025  
**Purpose**: Comprehensive guide to free news sources and sentiment analysis tools

---

## Table of Contents

1. [Free News Sources (RSS Feeds)](#free-news-sources-rss-feeds)
2. [Free Sentiment Analysis Models](#free-sentiment-analysis-models)
3. [Free APIs with Sentiment Analysis](#free-apis-with-sentiment-analysis)
4. [Open Source Tools](#open-source-tools)
5. [Recommended Setup](#recommended-setup)

---

## Free News Sources (RSS Feeds)

### Indian Financial News Sources

#### 1. Economic Times RSS Feeds
- **Base URL**: `https://economictimes.indiatimes.com/rssfeeds/`
- **Specific Feeds**:
  - Markets: `https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms`
  - Economy: `https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms`
  - Policy: `https://economictimes.indiatimes.com/news/policy/rssfeeds/1052732854.cms`
  - Companies: `https://economictimes.indiatimes.com/companies/rssfeeds/2147476.cms`
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Full articles with titles, descriptions, and publication dates
- **Limitations**: None for RSS feeds

#### 2. Moneycontrol RSS Feeds
- **Base URL**: `https://www.moneycontrol.com/rss/`
- **Specific Feeds**:
  - Latest News: `https://www.moneycontrol.com/rss/latestnews.xml`
  - Market News: `https://www.moneycontrol.com/rss/marketreports.xml`
  - Business News: `https://www.moneycontrol.com/rss/business.xml`
  - Economy: `https://www.moneycontrol.com/rss/economy.xml`
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Headlines, summaries, and links to full articles
- **Limitations**: None for RSS feeds

#### 3. Business Standard RSS Feeds
- **Base URL**: `https://www.business-standard.com/rss/`
- **Specific Feeds**:
  - Markets: `https://www.business-standard.com/rss/markets-106.rss`
  - Economy: `https://www.business-standard.com/rss/economy-102.rss`
  - Companies: `https://www.business-standard.com/rss/companies-103.rss`
  - Policy: `https://www.business-standard.com/rss/policy-104.rss`
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Full article summaries
- **Limitations**: None for RSS feeds

#### 4. Livemint RSS Feeds
- **Base URL**: `https://www.livemint.com/rss/`
- **Specific Feeds**:
  - Markets: `https://www.livemint.com/rss/markets`
  - Companies: `https://www.livemint.com/rss/companies`
  - Economy: `https://www.livemint.com/rss/economy`
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Article summaries and links
- **Limitations**: None for RSS feeds

#### 5. Financial Express RSS Feeds
- **Base URL**: `https://www.financialexpress.com/feed/`
- **Specific Feeds**:
  - Markets: `https://www.financialexpress.com/market/feed/`
  - Economy: `https://www.financialexpress.com/economy/feed/`
  - Companies: `https://www.financialexpress.com/companies/feed/`
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Full article content in RSS
- **Limitations**: None for RSS feeds

#### 6. NSE Corporate Announcements
- **URL**: `https://www.nseindia.com/api/corporate-announcements`
- **Coverage**: Corporate actions, results, board meetings, AGMs
- **Cost**: Free
- **Update Frequency**: Real-time during market hours
- **Content**: Structured JSON data
- **Limitations**: Requires proper headers (User-Agent) to avoid blocking

#### 7. BSE Corporate Announcements
- **URL**: `https://www.bseindia.com/corporates/List_Scrips.aspx`
- **Coverage**: Corporate announcements, results
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: HTML/structured data
- **Limitations**: May require web scraping

### International Free News Sources

#### 8. Yahoo Finance RSS
- **URL**: `https://feeds.finance.yahoo.com/rss/2.0/headline`
- **Coverage**: Global financial news
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Headlines and summaries
- **Limitations**: Limited to headlines, may need to fetch full articles

#### 9. Google News RSS (Financial)
- **URL**: `https://news.google.com/rss/search?q=finance+india+stock+market`
- **Coverage**: Aggregated financial news
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Headlines and summaries
- **Limitations**: Aggregated content, may have duplicates

#### 10. Reddit Finance (via RSS)
- **URL**: `https://www.reddit.com/r/IndianStockMarket/.rss`
- **Coverage**: Community discussions and news
- **Cost**: Free
- **Update Frequency**: Real-time
- **Content**: Discussion threads
- **Limitations**: User-generated content, may need filtering

---

## Free Sentiment Analysis Models

### 1. FinBERT (Hugging Face)
- **Model**: `yiyanghkust/finbert-tone`
- **Type**: Pre-trained BERT model for financial sentiment
- **Cost**: Free (open source)
- **Language**: English
- **Accuracy**: ~85-90% on financial text
- **Speed**: ~10-50ms per article
- **Installation**:
  ```bash
  pip install transformers torch
  ```
- **Usage**: Direct Python library, no API calls needed
- **Limitations**: 
  - Trained on Western financial news (may need fine-tuning for Indian context)
  - 512 token limit
  - Binary/ternary classification (positive/negative/neutral)

### 2. VADER Sentiment (NLTK)
- **Library**: NLTK VADER
- **Type**: Rule-based sentiment analyzer
- **Cost**: Free
- **Language**: English
- **Accuracy**: ~70-75% on general text
- **Speed**: ~1-5ms per article
- **Installation**:
  ```bash
  pip install nltk
  python -c "import nltk; nltk.download('vader_lexicon')"
  ```
- **Usage**: Simple Python library
- **Limitations**: 
  - Not specifically trained for financial text
  - Less accurate than ML models
  - No context understanding

### 3. TextBlob Sentiment
- **Library**: TextBlob
- **Type**: Pattern-based sentiment analysis
- **Cost**: Free
- **Language**: English
- **Accuracy**: ~65-70% on general text
- **Speed**: ~1-3ms per article
- **Installation**:
  ```bash
  pip install textblob
  ```
- **Usage**: Very simple API
- **Limitations**: 
  - Basic sentiment only
  - Not financial-specific
  - Low accuracy

### 4. DeepSeek R1 7B (Local - Free)
- **Model**: `deepseek-r1:7b` (via Ollama)
- **Type**: Large Language Model
- **Cost**: Free (runs locally)
- **Language**: Multi-language (including English)
- **Accuracy**: ~85-90% with proper prompting
- **Speed**: ~2-5 seconds per article
- **Installation**: Already in your system
- **Usage**: Via OllamaService
- **Advantages**: 
  - Excellent context understanding
  - Can understand complex financial concepts
  - Structured JSON output
  - No API limits

### 5. Qwen2.5 7B (Local - Free)
- **Model**: `qwen2.5:7b` (via Ollama)
- **Type**: Large Language Model
- **Cost**: Free (runs locally)
- **Language**: Multi-language
- **Accuracy**: ~80-85%
- **Speed**: ~1-3 seconds per article
- **Installation**: Already in your system
- **Usage**: Via OllamaService (fallback model)

---

## Free APIs with Sentiment Analysis

### 1. Alpha Vantage News & Sentiment API
- **URL**: `https://www.alphavantage.co/query`
- **Free Tier**: 5 API calls per minute, 500 calls per day
- **Features**: 
  - News articles with sentiment scores
  - Topic tagging
  - Relevance scoring
- **Cost**: Free (with limits)
- **Limitations**: 
  - Rate limited (5 calls/min)
  - Daily limit (500 calls)
  - May not cover all Indian stocks

### 2. NewsAPI
- **URL**: `https://newsapi.org/`
- **Free Tier**: 100 requests per day
- **Features**: 
  - News aggregation
  - No built-in sentiment (need to add your own)
- **Cost**: Free (limited)
- **Limitations**: 
  - 100 requests/day
  - No sentiment analysis included
  - Need to implement sentiment yourself

### 3. GNews API
- **URL**: `https://gnews.io/api/v4/`
- **Free Tier**: 100 requests per day
- **Features**: 
  - News aggregation
  - No built-in sentiment
- **Cost**: Free (limited)
- **Limitations**: 
  - 100 requests/day
  - No sentiment analysis
  - Need to add sentiment analysis

### 4. Stockgeist API (Free Tier)
- **URL**: `https://stockgeist.ai/`
- **Free Tier**: Limited requests
- **Features**: 
  - Stock sentiment analysis
  - News aggregation
  - Social media sentiment
- **Cost**: Free tier available
- **Limitations**: 
  - Limited requests
  - May not cover all Indian stocks
  - Requires API key

### 5. Senti API (Free Tier)
- **URL**: `https://getsenti.ai/`
- **Free Tier**: Limited access
- **Features**: 
  - AI-powered sentiment analysis
  - Reddit/YouTube sentiment
  - Word maps and trends
- **Cost**: Free tier available
- **Limitations**: 
  - Limited to free tier features
  - May focus on US markets

---

## Open Source Tools

### 1. Stockpulse-AI (GitHub)
- **Repository**: `github.com/amitpatole/stockpulse-ai`
- **Type**: Complete stock news monitoring system
- **Cost**: Free (open source)
- **Features**: 
  - Tracks 10+ free news sources
  - AI analysis and ratings
  - Technical and sentiment signals
- **Installation**: Clone from GitHub
- **Limitations**: 
  - Need to set up and maintain
  - May require customization for Indian markets

### 2. NewsAPI Python Client
- **Library**: `newsapi-python`
- **Type**: Python wrapper for news APIs
- **Cost**: Free
- **Features**: 
  - Easy integration
  - Multiple source support
- **Installation**:
  ```bash
  pip install newsapi-python
  ```

### 3. Feedparser (RSS Parser)
- **Library**: `feedparser`
- **Type**: RSS/Atom feed parser
- **Cost**: Free
- **Features**: 
  - Parse any RSS feed
  - Extract article content
- **Installation**:
  ```bash
  pip install feedparser
  ```

---

## Recommended Setup for Your System

### Option 1: Fully Free Setup (Recommended)

**News Sources**:
1. Economic Times RSS (markets, economy, policy)
2. Moneycontrol RSS (markets, stocks)
3. Business Standard RSS (economy, policy)
4. NSE Corporate Announcements API

**Sentiment Analysis**:
1. **Primary**: DeepSeek R1 7B (already in your system)
   - Best for complex macro/government news
   - Excellent reasoning capabilities
   - No API costs
   
2. **Secondary**: FinBERT (optional, for speed)
   - Fast processing for simple news
   - Free and open source
   - Can be added later for optimization

**Total Cost**: $0/month

**Advantages**:
- No API rate limits (except NSE headers)
- No daily/monthly quotas
- Full control over data
- No external dependencies

**Implementation**:
```python
# Free news sources configuration
FREE_NEWS_SOURCES = [
    {
        "name": "economic_times",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "type": "rss",
        "cost": "free"
    },
    {
        "name": "moneycontrol",
        "url": "https://www.moneycontrol.com/rss/latestnews.xml",
        "type": "rss",
        "cost": "free"
    },
    {
        "name": "business_standard",
        "url": "https://www.business-standard.com/rss/markets-106.rss",
        "type": "rss",
        "cost": "free"
    },
    {
        "name": "nse_announcements",
        "url": "https://www.nseindia.com/api/corporate-announcements",
        "type": "api",
        "cost": "free",
        "headers_required": True
    }
]

# Free sentiment analysis
SENTIMENT_ANALYSIS = {
    "primary": "deepseek-r1:7b",  # Already in system
    "secondary": "finbert",  # Optional, for speed
    "cost": "free"
}
```

### Option 2: Hybrid Setup (Free + Optional Paid)

**News Sources**: Same as Option 1 (all free)

**Sentiment Analysis**:
1. **Primary**: DeepSeek R1 7B (free, local)
2. **Optional Enhancement**: Alpha Vantage API (free tier)
   - Use for additional news coverage
   - 500 calls/day free tier
   - Can supplement RSS feeds

**Total Cost**: $0/month (or minimal if using Alpha Vantage paid tier later)

---

## Comparison Table

| Source | Type | Cost | Speed | Accuracy | Indian Market Coverage |
|--------|------|------|-------|----------|----------------------|
| **Economic Times RSS** | News | Free | Real-time | High | Excellent |
| **Moneycontrol RSS** | News | Free | Real-time | High | Excellent |
| **Business Standard RSS** | News | Free | Real-time | High | Excellent |
| **NSE Announcements** | Corporate | Free | Real-time | High | Excellent |
| **DeepSeek R1 7B** | Sentiment | Free | 2-5s | 85-90% | Good (via prompting) |
| **FinBERT** | Sentiment | Free | 10-50ms | 85-90% | Good (may need fine-tuning) |
| **Alpha Vantage API** | News+Sentiment | Free tier | Fast | 80-85% | Limited |
| **VADER** | Sentiment | Free | 1-5ms | 70-75% | Basic |

---

## Implementation Priority

### Phase 1: Start with Free RSS Feeds
1. Economic Times RSS
2. Moneycontrol RSS
3. Business Standard RSS

### Phase 2: Add Sentiment Analysis
1. Use DeepSeek R1 7B (already available)
2. Optionally add FinBERT for speed optimization

### Phase 3: Add Corporate Announcements
1. NSE Corporate Announcements API
2. BSE announcements (if needed)

### Phase 4: Optional Enhancements
1. Alpha Vantage API (free tier) for additional coverage
2. Reddit/YouTube sentiment (if needed)

---

## Cost Breakdown

### Fully Free Setup
- **News Sources**: $0 (RSS feeds)
- **Sentiment Analysis**: $0 (local LLM)
- **Storage**: $0 (SQLite)
- **Total**: **$0/month**

### With Optional Enhancements
- **News Sources**: $0 (RSS feeds)
- **Sentiment Analysis**: $0 (local LLM)
- **Alpha Vantage API**: $0 (free tier) or $49/month (paid)
- **Total**: **$0-49/month** (depending on needs)

---

## Best Practices

1. **Respect Rate Limits**: Even free RSS feeds should be fetched at reasonable intervals (15-30 minutes)
2. **User-Agent Headers**: Always set proper User-Agent headers to avoid blocking
3. **Error Handling**: Implement retry logic for network failures
4. **Deduplication**: Remove duplicate articles from multiple sources
5. **Caching**: Cache article content to avoid re-processing
6. **Monitoring**: Track source availability and update frequency

---

## Conclusion

You can build a complete sentiment analysis system using **100% free sources**:

- **News**: RSS feeds from major Indian financial news sources
- **Sentiment Analysis**: DeepSeek R1 7B (already in your system) + optional FinBERT
- **Storage**: SQLite (already in use)

This setup provides excellent coverage of Indian stock market news with high-quality sentiment analysis, all at zero cost.

---

**Next Steps**:
- Review [Sentiment Analysis System](09_SENTIMENT_ANALYSIS_SYSTEM.md) for implementation details
- Check [Agent Implementation Guide](03_AGENT_IMPLEMENTATION_GUIDE.md) for News Sentiment Analyst agent
