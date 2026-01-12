"""Unit tests for fetch_and_store_news.py functions."""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from scripts.fetch_and_store_news import (
    normalize_datetime,
    filter_articles_by_date,
    store_articles_bulk
)
from database.repositories.sentiment_repo import SentimentRepository


class TestNormalizeDatetime:
    """Test normalize_datetime function."""
    
    def test_naive_datetime(self):
        """Test with naive datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = normalize_datetime(dt)
        assert result == dt
        assert result.tzinfo is None
    
    def test_timezone_aware_datetime(self):
        """Test with timezone-aware datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))  # IST
        result = normalize_datetime(dt)
        assert result.tzinfo is None
        # Should be converted to UTC (subtract 5:30 hours)
        assert result.hour == 5  # 10:30 IST = 5:00 UTC
    
    def test_none_input(self):
        """Test with None input."""
        result = normalize_datetime(None)
        assert result is None
    
    def test_utc_timezone(self):
        """Test with UTC timezone."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = normalize_datetime(dt)
        assert result.tzinfo is None
        assert result == datetime(2024, 1, 15, 10, 30, 0)


class TestFilterArticlesByDate:
    """Test filter_articles_by_date function."""
    
    def test_no_filters(self):
        """Test with no date filters."""
        articles = [
            {'title': 'Article 1', 'published_date': datetime.now()},
            {'title': 'Article 2', 'published_date': datetime.now() - timedelta(days=5)}
        ]
        result = filter_articles_by_date(articles)
        assert len(result) == 2
    
    def test_start_date_filter(self):
        """Test filtering by start date."""
        now = datetime.now()
        articles = [
            {'title': 'Recent', 'published_date': now},
            {'title': 'Old', 'published_date': now - timedelta(days=5)}
        ]
        start_date = now - timedelta(days=2)
        result = filter_articles_by_date(articles, start_date=start_date)
        assert len(result) == 1
        assert result[0]['title'] == 'Recent'
    
    def test_end_date_filter(self):
        """Test filtering by end date."""
        now = datetime.now()
        articles = [
            {'title': 'Recent', 'published_date': now},
            {'title': 'Old', 'published_date': now - timedelta(days=5)}
        ]
        end_date = now - timedelta(days=2)
        result = filter_articles_by_date(articles, end_date=end_date)
        assert len(result) == 1
        assert result[0]['title'] == 'Old'
    
    def test_date_range_filter(self):
        """Test filtering by date range."""
        now = datetime.now()
        articles = [
            {'title': 'Recent', 'published_date': now},
            {'title': 'Middle', 'published_date': now - timedelta(days=2)},
            {'title': 'Old', 'published_date': now - timedelta(days=5)}
        ]
        start_date = now - timedelta(days=3)
        end_date = now - timedelta(days=1)
        result = filter_articles_by_date(articles, start_date=start_date, end_date=end_date)
        assert len(result) == 1
        assert result[0]['title'] == 'Middle'
    
    def test_article_without_date(self):
        """Test article without published_date."""
        articles = [
            {'title': 'Article 1', 'published_date': datetime.now()},
            {'title': 'Article 2'}  # No date
        ]
        # When no filters, all articles are returned (including those without dates)
        result = filter_articles_by_date(articles)
        assert len(result) == 2  # Both articles returned when no filters
        
        # Test with filters - articles without dates should be excluded
        result_filtered = filter_articles_by_date(articles, start_date=datetime.now() - timedelta(days=1))
        assert len(result_filtered) == 1
        assert result_filtered[0]['title'] == 'Article 1'
    
    def test_empty_list(self):
        """Test with empty list."""
        result = filter_articles_by_date([])
        assert result == []


class TestStoreArticlesBulk:
    """Test store_articles_bulk function."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = Mock(spec=SentimentRepository)
        return repo
    
    def test_empty_articles(self, mock_repo):
        """Test with empty articles list."""
        stored, updated, skipped = store_articles_bulk(mock_repo, [], set())
        assert stored == 0
        assert updated == 0
        assert skipped == 0
    
    def test_articles_without_urls(self, mock_repo):
        """Test articles without URLs."""
        articles = [
            {'title': 'Article 1'},  # No URL
            {'title': 'Article 2', 'url': 'url1'}
        ]
        mock_repo.bulk_store_articles.return_value = (1, 0)
        
        stored, updated, skipped = store_articles_bulk(mock_repo, articles, set())
        assert stored == 1
        assert skipped == 1  # One without URL
    
    def test_new_articles(self, mock_repo):
        """Test storing new articles."""
        articles = [
            {'title': 'Article 1', 'url': 'url1', 'published_date': datetime.now()},
            {'title': 'Article 2', 'url': 'url2', 'published_date': datetime.now()}
        ]
        mock_repo.bulk_store_articles.return_value = (2, 0)
        
        stored, updated, skipped = store_articles_bulk(mock_repo, articles, set())
        assert stored == 2
        assert updated == 0
        assert skipped == 0
    
    def test_existing_articles_skip(self, mock_repo):
        """Test skipping existing articles."""
        articles = [
            {'title': 'Article 1', 'url': 'url1', 'published_date': datetime.now()},
            {'title': 'Article 2', 'url': 'url2', 'published_date': datetime.now()}
        ]
        existing_urls = {'url1'}
        mock_repo.bulk_store_articles.return_value = (1, 0)
        
        stored, updated, skipped = store_articles_bulk(mock_repo, articles, existing_urls)
        assert stored == 1
        assert skipped == 1  # url1 already exists
    
    def test_force_refresh(self, mock_repo):
        """Test force refresh mode."""
        articles = [
            {'title': 'Article 1', 'url': 'url1', 'published_date': datetime.now()}
        ]
        existing_urls = {'url1'}
        mock_repo.bulk_store_articles.return_value = (0, 1)
        
        stored, updated, skipped = store_articles_bulk(mock_repo, articles, existing_urls, force_refresh=True)
        assert stored == 0
        assert updated == 1
        assert skipped == 0  # No skip in force refresh
