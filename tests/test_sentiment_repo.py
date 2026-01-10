"""Comprehensive unit tests for SentimentRepository."""
import pytest
from datetime import datetime, date, timedelta, timezone
from database.repositories.sentiment_repo import SentimentRepository
from database.models import NewsArticle, SentimentScore, MacroStockSentiment, NewsSource, Stock
from config.constants import Exchange


class TestSentimentRepository:
    """Test cases for SentimentRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create SentimentRepository instance."""
        return SentimentRepository(temp_db)
    
    @pytest.fixture
    def sample_stock(self, temp_db):
        """Create sample stock."""
        stock = Stock(
            symbol="TEST-EQ",
            name="Test Stock",
            exchange=Exchange.NSE,
            sector="IT",
            market_cap=1000000000
        )
        temp_db.add(stock)
        temp_db.commit()
        temp_db.refresh(stock)
        return stock
    
    @pytest.fixture
    def sample_news_source(self, temp_db):
        """Create sample news source."""
        source = NewsSource(
            name="test_source",
            url_pattern="https://example.com/rss",
            is_active=True,
            fetch_frequency=15
        )
        temp_db.add(source)
        temp_db.commit()
        temp_db.refresh(source)
        return source
    
    # News Article Operations Tests
    
    def test_store_article_new(self, repo, sample_stock):
        """Test storing a new article."""
        article = repo.store_article(
            source="test_source",
            title="Test Article",
            content="Test content",
            url="https://example.com/article1",
            published_date=datetime.now(),
            stock_id=sample_stock.id,
            category="markets"
        )
        
        assert article.id is not None
        assert article.title == "Test Article"
        assert article.stock_id == sample_stock.id
    
    def test_store_article_update_existing(self, repo, sample_stock):
        """Test updating existing article."""
        # Store first time
        article1 = repo.store_article(
            source="test_source",
            title="Original Title",
            content="Original content",
            url="https://example.com/article1",
            published_date=datetime.now()
        )
        
        # Update with same URL
        article2 = repo.store_article(
            source="test_source",
            title="Updated Title",
            content="Updated content",
            url="https://example.com/article1",
            published_date=datetime.now(),
            stock_id=sample_stock.id
        )
        
        assert article1.id == article2.id
        assert article2.title == "Updated Title"
        assert article2.stock_id == sample_stock.id
    
    def test_get_articles_for_stock(self, repo, sample_stock):
        """Test getting articles for a stock."""
        # Add articles
        repo.store_article("test_source", "Article 1", "Content 1", "url1", datetime.now(), stock_id=sample_stock.id)
        repo.store_article("test_source", "Article 2", "Content 2", "url2", datetime.now(), stock_id=sample_stock.id)
        repo.store_article("test_source", "Article 3", "Content 3", "url3", datetime.now())  # No stock_id
        
        articles = repo.get_articles_for_stock(sample_stock.id)
        assert len(articles) == 2
        assert all(a.stock_id == sample_stock.id for a in articles)
    
    def test_get_sector_articles(self, repo, sample_stock):
        """Test getting articles for a sector."""
        # Add articles for IT sector stock
        repo.store_article("test_source", "Article 1", "Content 1", "url1", datetime.now(), stock_id=sample_stock.id)
        
        articles = repo.get_sector_articles("IT")
        assert len(articles) >= 1
    
    def test_get_macro_articles(self, repo):
        """Test getting macro articles."""
        repo.store_article(
            "test_source", "Macro Article", "Content", "url1", datetime.now(),
            is_macro=True, macro_category="economy"
        )
        
        articles = repo.get_macro_articles()
        assert len(articles) >= 1
        assert all(a.is_macro for a in articles)
    
    def test_get_recent_articles(self, repo):
        """Test getting recent articles."""
        now = datetime.now()
        repo.store_article("test_source", "Recent", "Content", "url1", now)
        repo.store_article("test_source", "Old", "Content", "url2", now - timedelta(days=2))
        
        articles = repo.get_recent_articles(days=1)
        assert len(articles) == 1
        assert articles[0].title == "Recent"
    
    def test_cleanup_old_articles(self, repo):
        """Test cleaning up old articles."""
        old_date = datetime.now() - timedelta(days=35)
        repo.store_article("test_source", "Old Article", "Content", "url1", old_date)
        repo.store_article("test_source", "Recent Article", "Content", "url2", datetime.now())
        
        deleted = repo.cleanup_old_articles(days=30)
        assert deleted >= 1
        
        articles = repo.get_recent_articles(days=100)
        assert len(articles) == 1
        assert articles[0].title == "Recent Article"
    
    # Sentiment Score Operations Tests
    
    def test_store_daily_sentiment(self, repo, sample_stock):
        """Test storing daily sentiment."""
        sentiment = repo.store_daily_sentiment(
            stock_id=sample_stock.id,
            sentiment_date=date.today(),
            overall_sentiment=0.75,
            confidence=0.85,
            article_count=10,
            positive_count=7,
            negative_count=2,
            neutral_count=1
        )
        
        assert sentiment.id is not None
        assert sentiment.overall_sentiment == 0.75
        assert sentiment.confidence == 0.85
    
    def test_get_sentiment_for_stock(self, repo, sample_stock):
        """Test getting sentiment for a stock."""
        today = date.today()
        repo.store_daily_sentiment(sample_stock.id, today, 0.75, 0.85, 10, 7, 2, 1)
        repo.store_daily_sentiment(sample_stock.id, today - timedelta(days=1), 0.65, 0.80, 8, 5, 2, 1)
        
        sentiment = repo.get_sentiment_for_stock(sample_stock.id)
        assert sentiment is not None
        assert sentiment.overall_sentiment == 0.75
        
        # Get specific date
        old_sentiment = repo.get_sentiment_for_stock(sample_stock.id, today - timedelta(days=1))
        assert old_sentiment.overall_sentiment == 0.65
    
    def test_get_macro_sentiment_for_stock(self, repo, sample_stock):
        """Test getting macro sentiment for a stock."""
        # Create article and mapping
        article = repo.store_article(
            "test_source", "Macro News", "Content", "url1", datetime.now(),
            is_macro=True
        )
        
        mappings = [{
            'news_article_id': article.id,
            'stock_id': sample_stock.id,
            'macro_sentiment': 0.6,
            'sector_impact': 0.7,
            'stock_sentiment': 0.65
        }]
        repo.store_macro_sentiment_mappings(mappings)
        
        macro_sentiment = repo.get_macro_sentiment_for_stock(sample_stock.id)
        assert macro_sentiment == 0.65
    
    # News Source Operations Tests
    
    def test_get_source_last_fetched(self, repo, sample_news_source):
        """Test getting source last fetched timestamp."""
        now = datetime.now()
        repo.update_source_last_fetched("test_source", now)
        
        last_fetched = repo.get_source_last_fetched("test_source")
        assert last_fetched is not None
        assert abs((last_fetched - now).total_seconds()) < 1
    
    def test_get_source_last_fetched_nonexistent(self, repo):
        """Test getting last fetched for non-existent source."""
        result = repo.get_source_last_fetched("nonexistent")
        assert result is None
    
    def test_get_latest_article_date_for_source(self, repo, sample_news_source):
        """Test getting latest article date for source."""
        now = datetime.now()
        repo.store_article("test_source", "Article 1", "Content", "url1", now)
        repo.store_article("test_source", "Article 2", "Content", "url2", now - timedelta(hours=1))
        
        latest = repo.get_latest_article_date_for_source("test_source")
        assert latest is not None
        assert abs((latest - now).total_seconds()) < 60
    
    def test_get_latest_article_date_global(self, repo):
        """Test getting latest article date globally."""
        now = datetime.now()
        repo.store_article("source1", "Article 1", "Content", "url1", now - timedelta(hours=1))
        repo.store_article("source2", "Article 2", "Content", "url2", now)
        
        latest = repo.get_latest_article_date()
        assert latest is not None
        assert abs((latest - now).total_seconds()) < 60
    
    def test_get_source_status(self, repo, sample_news_source):
        """Test getting source status."""
        now = datetime.now()
        repo.update_source_last_fetched("test_source", now)
        repo.store_article("test_source", "Article", "Content", "url1", now)
        
        status = repo.get_source_status("test_source")
        assert status['exists'] is True
        assert status['is_active'] is True
        assert status['last_fetched'] is not None
        assert status['article_count'] >= 1
    
    def test_get_source_status_nonexistent(self, repo):
        """Test getting status for non-existent source."""
        status = repo.get_source_status("nonexistent")
        assert status['exists'] is False
        assert status['article_count'] == 0
    
    def test_get_all_sources_status(self, repo, sample_news_source):
        """Test getting all sources status."""
        statuses = repo.get_all_sources_status()
        assert len(statuses) >= 1
        assert any(s['source_name'] == "test_source" for s in statuses)
    
    def test_get_source_fetch_start_date_with_history(self, repo, sample_news_source):
        """Test getting fetch start date with history."""
        now = datetime.now()
        repo.update_source_last_fetched("test_source", now - timedelta(hours=2))
        repo.store_article("test_source", "Article", "Content", "url1", now - timedelta(hours=1))
        
        start_date = repo.get_source_fetch_start_date("test_source")
        # Should be most recent minus 1 hour buffer
        assert start_date is not None
        assert start_date < now
    
    def test_get_source_fetch_start_date_no_history(self, repo):
        """Test getting fetch start date with no history."""
        start_date = repo.get_source_fetch_start_date("new_source", default_days=30)
        assert start_date is not None
        assert (datetime.now() - start_date).days <= 30
    
    def test_update_source_last_fetched(self, repo, sample_news_source):
        """Test updating source last fetched."""
        now = datetime.now()
        repo.update_source_last_fetched("test_source", now)
        
        last_fetched = repo.get_source_last_fetched("test_source")
        assert last_fetched is not None
        assert abs((last_fetched - now).total_seconds()) < 1
    
    def test_get_existing_urls(self, repo):
        """Test getting existing URLs."""
        repo.store_article("test_source", "Article 1", "Content", "url1", datetime.now())
        repo.store_article("test_source", "Article 2", "Content", "url2", datetime.now())
        
        urls = repo.get_existing_urls()
        assert len(urls) >= 2
        assert "url1" in urls
        assert "url2" in urls
    
    def test_get_existing_urls_with_date_filter(self, repo):
        """Test getting existing URLs with date filter."""
        old_date = datetime.now() - timedelta(days=2)
        repo.store_article("test_source", "Old", "Content", "url1", old_date)
        repo.store_article("test_source", "Recent", "Content", "url2", datetime.now())
        
        urls = repo.get_existing_urls(since_date=datetime.now() - timedelta(days=1))
        assert "url2" in urls
        assert "url1" not in urls
    
    def test_bulk_store_articles_new(self, repo):
        """Test bulk storing new articles."""
        articles = [
            {
                'source': 'test_source',
                'title': 'Article 1',
                'content': 'Content 1',
                'url': 'url1',
                'published_date': datetime.now()
            },
            {
                'source': 'test_source',
                'title': 'Article 2',
                'content': 'Content 2',
                'url': 'url2',
                'published_date': datetime.now()
            }
        ]
        
        inserted, updated = repo.bulk_store_articles(articles)
        assert inserted == 2
        assert updated == 0
    
    def test_bulk_store_articles_update(self, repo):
        """Test bulk storing with updates."""
        # Store first time
        repo.store_article("test_source", "Original", "Content", "url1", datetime.now())
        
        # Update via bulk
        articles = [{
            'source': 'test_source',
            'title': 'Updated',
            'content': 'New Content',
            'url': 'url1',
            'published_date': datetime.now()
        }]
        
        inserted, updated = repo.bulk_store_articles(articles, force_refresh=True)
        assert inserted == 0
        assert updated == 1
        
        # Verify update
        article = repo.session.query(NewsArticle).filter(NewsArticle.url == "url1").first()
        assert article.title == "Updated"
    
    def test_bulk_store_articles_skip_existing(self, repo):
        """Test bulk storing skips existing URLs."""
        # Store first time
        repo.store_article("test_source", "Original", "Content", "url1", datetime.now())
        
        # Try to store again (should skip)
        articles = [{
            'source': 'test_source',
            'title': 'New Title',
            'content': 'New Content',
            'url': 'url1',
            'published_date': datetime.now()
        }]
        
        existing_urls = repo.get_existing_urls()
        inserted, updated = repo.bulk_store_articles(articles, existing_urls=existing_urls)
        assert inserted == 0
        assert updated == 0
    
    def test_get_stock_sector(self, repo, sample_stock):
        """Test getting stock sector."""
        sector = repo.get_stock_sector(sample_stock.id)
        assert sector == "IT"
    
    def test_get_all_stocks_with_sectors(self, repo, sample_stock):
        """Test getting all stocks with sectors."""
        stocks = repo.get_all_stocks_with_sectors()
        assert len(stocks) >= 1
        assert any(s['symbol'] == "TEST-EQ" for s in stocks)
        assert any(s['sector'] == "IT" for s in stocks)
    
    def test_store_macro_sentiment_mappings(self, repo, sample_stock):
        """Test storing macro sentiment mappings."""
        article = repo.store_article(
            "test_source", "Macro News", "Content", "url1", datetime.now(),
            is_macro=True
        )
        
        mappings = [{
            'news_article_id': article.id,
            'stock_id': sample_stock.id,
            'macro_sentiment': 0.6,
            'sector_impact': 0.7,
            'stock_sentiment': 0.65
        }]
        
        stored = repo.store_macro_sentiment_mappings(mappings)
        assert len(stored) == 1
        assert stored[0].stock_sentiment == 0.65
    
    def test_cleanup_old_macro_mappings(self, repo, sample_stock):
        """Test cleaning up old macro mappings."""
        article = repo.store_article(
            "test_source", "Macro News", "Content", "url1", datetime.now(),
            is_macro=True
        )
        
        # Create old mapping (simulate by setting created_at)
        mapping = MacroStockSentiment(
            news_article_id=article.id,
            stock_id=sample_stock.id,
            macro_sentiment=0.6,
            sector_impact=0.7,
            stock_sentiment=0.65
        )
        repo.session.add(mapping)
        repo.session.commit()
        
        # Manually set old date (for testing)
        old_date = datetime.now() - timedelta(days=100)
        repo.session.query(MacroStockSentiment).filter(
            MacroStockSentiment.id == mapping.id
        ).update({'created_at': old_date})
        repo.session.commit()
        
        deleted = repo.cleanup_old_macro_mappings(days=90)
        assert deleted >= 1
