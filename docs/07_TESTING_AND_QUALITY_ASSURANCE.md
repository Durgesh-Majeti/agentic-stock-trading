# Testing & Quality Assurance Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [End-to-End Tests](#end-to-end-tests)
5. [Performance Tests](#performance-tests)
6. [Test Data](#test-data)
7. [CI/CD](#cicd)
8. [Quality Metrics](#quality-metrics)

---

## Testing Strategy

### Test Pyramid

```
        /\
       /E2E\      (Few, critical paths)
      /------\
     /Integration\ (Key workflows)
    /------------\
   /  Unit Tests  \ (Many, fast)
  /----------------\
```

### Test Types

1. **Unit Tests**: Individual components
2. **Integration Tests**: Component interactions
3. **E2E Tests**: Full workflows
4. **Performance Tests**: Load and stress
5. **Security Tests**: Vulnerability scanning

---

## Unit Tests

### News Fetcher Tests

**File**: `tests/test_news_fetcher.py`

**Coverage**:
- ✅ RSS feed parsing
- ✅ Article content extraction
- ✅ Date parsing (multiple formats)
- ✅ Article deduplication
- ✅ Error handling
- ✅ Source management

**Run Tests**:
```bash
pytest tests/test_news_fetcher.py -v
```

### Sentiment Repository Tests

**File**: `tests/test_sentiment_repo.py` (to be created)

**Coverage**:
- Article storage and retrieval
- Sentiment score storage
- Macro sentiment mapping
- Daily aggregation
- Cleanup operations

### Example: Database Librarian

```python
# tests/test_librarian.py
import pytest
from agents.database_librarian import DatabaseLibrarian

def test_translate_oversold_query():
    librarian = DatabaseLibrarian()
    sql = librarian.translate("oversold RSI stocks")
    
    assert "rsi" in sql.lower()
    assert "select" in sql.lower()
    assert "30" in sql or "rsi_14" in sql.lower()

def test_execute_query():
    librarian = DatabaseLibrarian()
    sql = "SELECT symbol FROM stocks LIMIT 1"
    results = librarian.execute(sql)
    
    assert isinstance(results, list)
    if results:
        assert "symbol" in results[0]
```

### Example: Data Scraper

```python
# tests/test_scraper.py
import pytest
from agents.data_scraper import DataScraper

def test_validate_data():
    scraper = DataScraper()
    
    valid_data = {
        "ltp": 100.0,
        "prev_close": 99.0,
        "timestamp": datetime.now()
    }
    assert scraper._validate_data(valid_data) == True
    
    invalid_data = {
        "ltp": 200.0,  # 100% deviation
        "prev_close": 100.0
    }
    assert scraper._validate_data(invalid_data) == False
```

---

## Integration Tests

### Example: Signal Generation Flow

```python
# tests/test_integration.py
import pytest
from agents.database_librarian import DatabaseLibrarian
from agents.data_scraper import DataScraper
from agents.strategy_specialist import StrategySpecialist

def test_signal_generation_flow():
    # Setup
    librarian = DatabaseLibrarian()
    scraper = DataScraper()
    strategy = StrategySpecialist()
    
    # Step 1: Get candidates
    candidates = librarian.process({
        "query": "oversold RSI stocks"
    })
    assert len(candidates["results"]) > 0
    
    # Step 2: Fetch data
    symbol = candidates["results"][0]["symbol"]
    data = scraper.process({"symbol": symbol})
    assert data["valid"] == True
    
    # Step 3: Generate signal
    signal = strategy.process(data["data"])
    assert "action" in signal
    assert "confidence" in signal
```

### Example: Sentiment Analysis Flow

```python
# tests/test_sentiment_integration.py
import pytest
from data_sources.news_fetcher import NewsFetcher
from database.repositories.sentiment_repo import SentimentRepository
from database.session import get_session

def test_sentiment_analysis_flow():
    # Setup
    fetcher = NewsFetcher()
    repo = SentimentRepository(next(get_session()))
    
    # Step 1: Fetch news
    articles = fetcher.fetch_all_sources(rate_limit=0)
    assert len(articles) > 0
    
    # Step 2: Store articles
    for article in articles[:5]:  # Test with 5 articles
        stored = repo.store_article(
            source=article['source'],
            title=article['title'],
            content=article['content'],
            url=article['url'],
            published_date=article['published_date']
        )
        assert stored.id is not None
    
    # Step 3: Get sentiment (would be done by agent)
    # This is a placeholder for agent implementation
```

---

## End-to-End Tests

### Example: Complete Trading Flow

```python
# tests/test_e2e.py
import pytest

def test_complete_trading_flow():
    # 1. User sends query via Telegram
    # 2. Librarian generates SQL
    # 3. Scraper fetches data
    # 4. Strategy generates signal
    # 5. Telegram sends for approval
    # 6. User approves
    # 7. Order executed
    # 8. Trade logged
    
    # Implementation depends on test framework
    pass
```

---

## Performance Tests

### Load Testing

```python
# tests/test_performance.py
import time
import pytest

def test_query_performance():
    librarian = DatabaseLibrarian()
    
    start = time.time()
    results = librarian.process({"query": "all stocks"})
    duration = time.time() - start
    
    assert duration < 1.0  # Should complete in < 1 second
    assert len(results["results"]) > 0
```

### Stress Testing

```python
def test_concurrent_requests():
    """Test system under load."""
    import concurrent.futures
    
    def make_request():
        librarian = DatabaseLibrarian()
        return librarian.process({"query": "oversold RSI"})
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
    
    assert all(r["count"] >= 0 for r in results)
```

---

## Test Data

### Sentiment Test Data

**Mock News Articles**:
```python
MOCK_ARTICLES = [
    {
        'source': 'economic_times',
        'title': 'TCS reports strong Q3 results',
        'content': 'TCS announced...',
        'url': 'https://example.com/tcs-q3',
        'published_date': datetime.now()
    },
    # ... more articles
]
```

### Fixtures

```python
# tests/conftest.py
import pytest
from database.session import get_session
from database.models import Stock, MarketDataDaily

@pytest.fixture
def db_session():
    """Create test database session."""
    session = get_session()
    yield session
    session.close()

@pytest.fixture
def sample_stock(db_session):
    """Create sample stock."""
    stock = Stock(symbol="TEST-EQ", name="Test Stock", exchange="NSE")
    db_session.add(stock)
    db_session.commit()
    return stock

@pytest.fixture
def sample_data(db_session, sample_stock):
    """Create sample market data."""
    data = MarketDataDaily(
        stock_id=sample_stock.id,
        date=date.today(),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000,
        rsi=28.5
    )
    db_session.add(data)
    db_session.commit()
    return data
```

---

## CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
```

---

## Quality Metrics

### Code Coverage

**Target**: > 80% coverage

```bash
pytest --cov=. --cov-report=html
```

### Performance Metrics

- **Signal Generation**: < 10 seconds
- **Database Queries**: < 100ms
- **API Calls**: < 5 seconds
- **Memory Usage**: < 4GB

### Quality Gates

- All tests passing
- Code coverage > 80%
- No critical security issues
- Performance within targets
- Documentation complete

---

**Next**: `08_MAINTENANCE_AND_UPGRADE.md`
