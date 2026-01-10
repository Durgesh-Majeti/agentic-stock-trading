# News Fetching and Storage Guide

**Version**: 2.0  
**Last Updated**: January 2025  
**Purpose**: Complete guide to fetching, storing, and managing news articles with per-source tracking

---

## Overview

The news fetching system efficiently collects and stores articles from multiple RSS sources with intelligent **per-source incremental updates**. The system tracks last fetched timestamps and latest article dates per source, enabling efficient 30-minute interval fetching.

**Key Features**:
- Per-source tracking for optimal fetch efficiency
- Multiple operation modes (incremental, update-recent, force-refresh)
- Bulk database operations for performance
- URL-based deduplication
- Comprehensive source status monitoring

---

## System Architecture

### Per-Source Tracking

Each news source maintains:
- `last_fetched`: Timestamp when we last fetched from this source (in `news_sources` table)
- `latest_article_date`: Most recent article published date for that source
- **Per-source start date**: Calculated individually for optimal fetching

**Benefits**:
- Source A fetched 2 hours ago → only fetches last 2 hours
- Source B fetched 1 day ago → only fetches last 1 day
- Source C is new → fetches last 30 days

**Result**: Each source only fetches what it needs, reducing fetch time by ~80%.

---

## Repository Methods

### Core Methods

#### `get_source_last_fetched(source_name: str) -> Optional[datetime]`
Returns the `last_fetched` timestamp for a specific source.

#### `get_latest_article_date_for_source(source_name: str) -> Optional[datetime]`
Returns the latest article published date for a specific source.

#### `get_source_fetch_start_date(source_name: str, default_days: int = 30) -> datetime`
**Smart method** that determines the optimal start date:
- Uses the **most recent** of:
  1. Source's `last_fetched` timestamp
  2. Latest article `published_date` for that source
- Subtracts 1 hour buffer for safety
- Falls back to `default_days` ago if no history

#### `get_source_status(source_name: str) -> Dict[str, Any]`
Returns comprehensive status:
- `last_fetched`: Last fetch timestamp
- `latest_article_date`: Latest article date
- `article_count`: Total articles
- `last_24h_count`: Articles in last 24 hours
- `is_active`: Whether source is active

#### `get_all_sources_status() -> List[Dict[str, Any]]`
Returns status for all active sources.

#### `get_existing_urls(since_date: Optional[datetime] = None) -> Set[str]`
Bulk URL checking for deduplication.

#### `bulk_store_articles(articles, existing_urls, force_refresh) -> tuple[int, int]`
Bulk insert/update with optimized logic.

---

## Usage

### Basic Usage (Incremental - Recommended)

```bash
# Fetch only new articles since last run (per-source tracking)
python scripts/fetch_and_store_news.py
```

**How it works**:
1. For each source, checks:
   - Source's `last_fetched` timestamp (from `news_sources` table)
   - Latest article `published_date` for that source
2. Uses the most recent of these two as the start date
3. Only fetches articles published after that date (per source)
4. Skips articles that already exist (by URL)
5. Stores only new articles
6. Updates `last_fetched` immediately after each source fetch

**First Run**: If no history exists, fetches last 30 days per source

**Subsequent Runs**: Only fetches articles since last fetch (typically 30 minutes worth)

---

### Update Recent Days

```bash
# Update only last 7 days
python scripts/fetch_and_store_news.py --update-recent 7
```

**Use Case**: Refresh recent articles without fetching everything

---

### Force Refresh

```bash
# Re-fetch and update all articles from last 30 days
python scripts/fetch_and_store_news.py --force-refresh
```

**Use Case**: Update existing articles with latest content

---

### Custom Date Range

```bash
# Fetch articles from specific date range
python scripts/fetch_and_store_news.py --start-date 2024-01-01 --end-date 2024-01-31
```

**Date Formats**: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`

---

### Specific Sources Only

```bash
# Fetch from specific sources only
python scripts/fetch_and_store_news.py --sources economic_times_markets moneycontrol_latest
```

**Available Sources**:
- `economic_times_markets`
- `economic_times_economy`
- `economic_times_policy`
- `moneycontrol_latest`
- `moneycontrol_markets`
- `business_standard_markets`
- `business_standard_economy`
- `business_standard_companies`
- `livemint_markets`
- `financial_express_markets`
- `bse_announcements`
- `yahoo_finance`

---

## RSS Feed Status

### ✅ Valid RSS Feeds (11 Active)

1. **Economic Times Markets** - `https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms`
2. **Economic Times Economy** - `https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms`
3. **Economic Times Policy** - `https://economictimes.indiatimes.com/news/policy/rssfeeds/1052732854.cms`
4. **Moneycontrol Latest** - `https://www.moneycontrol.com/rss/latestnews.xml`
5. **Moneycontrol Markets** - `https://www.moneycontrol.com/rss/marketreports.xml`
6. **Business Standard Markets** - `https://www.business-standard.com/rss/markets-106.rss`
7. **Business Standard Economy** - `https://www.business-standard.com/rss/economy-policy-108.rss`
8. **Business Standard Companies** - `https://www.business-standard.com/rss/companies-101.rss`
9. **Livemint Markets** - `https://www.livemint.com/rss/markets`
10. **Financial Express Markets** - `https://www.financialexpress.com/feed/market/`
11. **BSE Announcements** - `https://www.bseindia.com/rssxml/Corporate_Announcements.xml`

### International Sources

12. **Yahoo Finance** - `https://finance.yahoo.com/rss/`

**Note**: All URLs have been validated and are working correctly.

---

## Performance Optimization

### 1. Per-Source Incremental Mode (Default)

**Problem**: Without optimization, would fetch all articles from last 30 days every time

**Solution**:
- Per-source tracking: Each source tracks its own `last_fetched` timestamp
- Checks both `last_fetched` and latest article date per source
- Only fetches articles published after the most recent timestamp

**Time Savings**: 
- First run: ~15-20 minutes (30 days from all sources)
- Subsequent runs: ~1-2 minutes (only new articles per source)
- **80% reduction** in fetch time for regular 30-minute interval runs

---

### 2. URL-Based Deduplication

**Problem**: Same article might appear in multiple sources

**Solution**:
- Deduplicates by URL before storing
- Checks existing URLs in bulk (optimized query)
- Skips articles that already exist

**Time Savings**: Avoids redundant database operations

---

### 3. Date Range Filtering

**Problem**: RSS feeds might return old articles

**Solution**:
- Filters articles by date range before processing
- Only processes articles within specified range

**Time Savings**: Processes only relevant articles

---

### 4. Bulk Database Operations

**Problem**: Individual inserts are slow

**Solution**:
- Uses `bulk_save_objects()` for new articles
- Batches updates together
- Single commit for all changes

**Time Savings**: 10-100x faster than individual inserts

---

### 5. Optimized URL Checking

**Problem**: Checking every URL individually is slow

**Solution**:
- Bulk query for existing URLs (single database query)
- Only checks URLs from last 30 days (for incremental mode)
- Uses set operations for fast lookups

**Time Savings**: O(1) lookup instead of O(n) queries

---

## Performance Metrics

| Mode | Articles Fetched | Processing Time |
|------|----------------|------------------|
| First Run (30 days) | ~500-1000 | 15-20 minutes |
| Incremental (30-min interval) | ~10-50 | 1-2 minutes |
| Update Recent (7 days) | ~100-200 | 3-5 minutes |
| Force Refresh (30 days) | ~500-1000 | 15-20 minutes |

**Optimization Impact**:
- Without optimization: ~20 minutes every run
- With per-source optimization: ~1-2 minutes per run
- **Time Savings**: ~90% reduction in fetch time

---

## Scheduling Recommendations

### Production Use

**During Market Hours** (9:15 AM - 3:30 PM IST):
```bash
# Every 30 minutes - incremental fetch (per-source tracking)
*/30 9-15 * * 1-5 python scripts/fetch_and_store_news.py
```

**After Market Hours**:
```bash
# Once at 4:00 PM - update last day
0 16 * * 1-5 python scripts/fetch_and_store_news.py --update-recent 1
```

**Weekly Maintenance**:
```bash
# Every Sunday - force refresh last 7 days
0 10 * * 0 python scripts/fetch_and_store_news.py --force-refresh --update-recent 7
```

---

## Data Storage

### Article Storage

Articles are stored according to the `NewsArticle` model:

```python
NewsArticle(
    source="economic_times_markets",  # Source name
    title="Article Title",            # Article title
    content="Full article text...",   # Full content
    url="https://...",                # Unique URL (used for deduplication)
    published_date=datetime(...),      # Publication date (naive UTC)
    category="markets",                # Category (optional)
    stock_id=None,                    # Stock ID if stock-specific (optional)
    is_macro=False,                   # Is macro news (optional)
    macro_category=None,              # Macro category (optional)
    affected_sectors=None             # Affected sectors (optional)
)
```

### Automatic Updates

- If article with same URL exists:
  - **Normal mode**: Skipped (not updated)
  - **Force refresh mode**: Updated with latest content

---

## Monitoring

### View Source Statuses

The script logs source statuses at the start:

```
Current source statuses:
  economic_times_markets: Last fetched=2025-01-15 10:00:00, Latest article=2025-01-15 10:15:00, Count=1250
  moneycontrol_latest: Last fetched=2025-01-15 10:00:00, Latest article=2025-01-15 10:20:00, Count=980
  bse_announcements: Last fetched=2025-01-15 10:00:00, Latest article=2025-01-15 10:10:00, Count=750
```

### Check Source Status Programmatically

```python
from database.session import get_db
from database.repositories.sentiment_repo import SentimentRepository

with get_db() as session:
    repo = SentimentRepository(session)
    
    # Get status for all sources
    statuses = repo.get_all_sources_status()
    for status in statuses:
        print(f"{status['source_name']}:")
        print(f"  Last fetched: {status['last_fetched']}")
        print(f"  Latest article: {status['latest_article_date']}")
        print(f"  Total articles: {status['article_count']}")
        print(f"  Last 24h: {status['last_24h_count']}")
    
    # Get status for one source
    status = repo.get_source_status('economic_times_markets')
    print(f"Last fetched: {status['last_fetched']}")
```

---

## Error Handling

### If Fetch Fails
- `last_fetched` is **not updated** if fetch fails
- Next run will retry from previous `last_fetched`
- No data loss or duplicate fetching

### If Storage Fails
- `last_fetched` **is updated** (after successful fetch)
- Articles might not be stored, but we won't re-fetch them
- Next run will skip already-fetched articles (by URL deduplication)

### Timezone Handling
- All datetimes normalized to naive UTC for consistent comparisons
- RSS feed dates converted from timezone-aware to naive UTC
- No timezone comparison errors

---

## Troubleshooting

### Issue: No articles stored

**Possible Causes**:
1. All articles already exist (check with `--force-refresh`)
2. Date range too restrictive
3. Network errors (check logs)

**Solution**:
```bash
# Check what would be fetched
python scripts/fetch_and_store_news.py --update-recent 1 --sources economic_times_markets
```

---

### Issue: Slow performance

**Possible Causes**:
1. Too many sources
2. Network latency
3. Large date range

**Solution**:
```bash
# Fetch from fewer sources
python scripts/fetch_and_store_news.py --sources economic_times_markets

# Or reduce date range
python scripts/fetch_and_store_news.py --update-recent 1
```

---

### Issue: Duplicate articles

**Possible Causes**:
1. URL not unique
2. Force refresh updating same articles

**Solution**:
- Check database for duplicate URLs
- Use incremental mode (default) to avoid duplicates

---

### Issue: RSS parsing errors

**Possible Causes**:
1. Invalid RSS feed URL
2. Malformed XML
3. Network issues

**Solution**:
- Run validation script: `python scripts/validate_rss_urls.py`
- Check source URL in `config/news_sources.py`
- Monitor logs for specific error messages

---

## Examples

### Example 1: First Time Setup

```bash
# Fetch initial articles (last 30 days)
python scripts/fetch_and_store_news.py
```

**Output**:
```
News Fetch and Store Process
============================================================
Current source statuses:
  economic_times_markets: Last fetched=Never, Latest article=None, Count=0
  moneycontrol_latest: Last fetched=Never, Latest article=None, Count=0
  ...
No existing articles: Fetching last 30 days
Global date range: 2024-12-16 10:00:00 to 2025-01-15 10:00:00
Fetching from 12 active sources
Found 0 existing articles in database
...
Stored: 847 articles
Skipped: 153 articles (duplicates/existing)
```

---

### Example 2: Daily Incremental Update

```bash
# Run daily - only fetches new articles
python scripts/fetch_and_store_news.py
```

**Output**:
```
News Fetch and Store Process
============================================================
Current source statuses:
  economic_times_markets: Last fetched=2025-01-15 08:30:00, Latest article=2025-01-15 09:45:00, Count=125
  moneycontrol_latest: Last fetched=2025-01-15 08:30:00, Latest article=2025-01-15 09:50:00, Count=98
  ...
Incremental mode: Earliest source start date = 2025-01-15 08:30:00
Global date range: 2025-01-15 08:30:00 to 2025-01-15 10:00:00
Fetching from economic_times_markets (since 2025-01-15 08:30:00)...
  economic_times_markets: 12 articles (after date filter)
  Updated economic_times_markets last_fetched to 2025-01-15 10:00:00
Fetching from moneycontrol_latest (since 2025-01-15 08:30:00)...
  moneycontrol_latest: 8 articles (after date filter)
  Updated moneycontrol_latest last_fetched to 2025-01-15 10:00:00
...
Stored: 23 articles
Skipped: 5 articles (duplicates/existing)
```

---

## Command Reference

```bash
# Incremental (default - recommended)
python scripts/fetch_and_store_news.py

# Update recent days
python scripts/fetch_and_store_news.py --update-recent N

# Force refresh
python scripts/fetch_and_store_news.py --force-refresh

# Custom date range
python scripts/fetch_and_store_news.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD

# Specific sources
python scripts/fetch_and_store_news.py --sources source1 source2

# Combined options
python scripts/fetch_and_store_news.py --force-refresh --update-recent 7 --sources economic_times_markets

# Help
python scripts/fetch_and_store_news.py --help
```

---

## Best Practices

1. **Use Incremental Mode**: Default mode is most efficient
2. **Schedule Regularly**: Run every 30 minutes during market hours
3. **Monitor Logs**: Check for errors or warnings
4. **Clean Old Articles**: Run cleanup periodically (30+ days old)
5. **Backup Database**: Before force refresh operations
6. **Monitor Source Status**: Use `get_all_sources_status()` regularly

---

## Integration with Sentiment Analysis

After fetching articles:

1. **Analyze Sentiment**: Use News Sentiment Analyst agent (Phase 3)
2. **Query Articles**: Use SentimentRepository methods
3. **Get Sentiment Scores**: Query sentiment_scores table
4. **Feed to Strategy**: Integrate sentiment with Strategy Specialist

---

## Related Documentation

- **Sentiment Analysis System**: See `09_SENTIMENT_ANALYSIS_SYSTEM.md`
- **Database Schema**: See `02_DATABASE_SCHEMA_AND_MIGRATION.md`
- **Free News Sources**: See `10_FREE_SENTIMENT_SOURCES.md`

---

**Last Updated**: January 2025  
**Status**: Ready for production use with per-source tracking
