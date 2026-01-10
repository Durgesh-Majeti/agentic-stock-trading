"""Tests for news fetcher module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from data_sources.news_fetcher import NewsFetcher
from config.news_sources import NewsSourceConfig


class TestNewsFetcher:
    """Test cases for NewsFetcher."""
    
    @pytest.fixture
    def news_fetcher(self):
        """Create NewsFetcher instance."""
        return NewsFetcher()
    
    @pytest.fixture
    def sample_rss_source(self):
        """Create sample RSS source config."""
        return NewsSourceConfig(
            name="test_rss",
            url="https://example.com/rss",
            type="rss",
            categories=["markets"],
            fetch_frequency=15
        )
    
    @pytest.fixture
    def sample_rss_feed(self):
        """Sample RSS feed data."""
        return {
            'entries': [
                {
                    'title': 'Test Article 1',
                    'link': 'https://example.com/article1',
                    'published': 'Mon, 01 Jan 2024 12:00:00 +0000',
                    'summary': 'Test summary 1',
                    'description': 'Test description 1'
                },
                {
                    'title': 'Test Article 2',
                    'link': 'https://example.com/article2',
                    'published': 'Tue, 02 Jan 2024 12:00:00 +0000',
                    'summary': 'Test summary 2'
                }
            ]
        }
    
    def test_init(self, news_fetcher):
        """Test NewsFetcher initialization."""
        assert news_fetcher is not None
        assert news_fetcher.session is not None
    
    @patch('data_sources.news_fetcher.feedparser')
    def test_fetch_rss_success(self, mock_feedparser, news_fetcher, sample_rss_source, sample_rss_feed):
        """Test successful RSS fetch."""
        # Mock feedparser
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = sample_rss_feed['entries']
        mock_feedparser.parse.return_value = mock_feed
        
        # Fetch articles
        articles = news_fetcher._fetch_rss(sample_rss_source)
        
        # Verify
        assert len(articles) == 2
        assert articles[0]['title'] == 'Test Article 1'
        assert articles[0]['url'] == 'https://example.com/article1'
        assert articles[0]['source'] == 'test_rss'
    
    @patch('data_sources.news_fetcher.feedparser')
    def test_fetch_rss_bozo_error(self, mock_feedparser, news_fetcher, sample_rss_source):
        """Test RSS fetch with parsing error."""
        # Mock feedparser with error
        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = Exception("Parse error")
        mock_feedparser.parse.return_value = mock_feed
        
        # Fetch articles
        articles = news_fetcher._fetch_rss(sample_rss_source)
        
        # Should return empty list
        assert articles == []
    
    def test_parse_date_rss_format(self, news_fetcher):
        """Test date parsing for RSS format."""
        date_str = "Mon, 01 Jan 2024 12:00:00 +0000"
        result = news_fetcher._parse_date(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_date_iso_format(self, news_fetcher):
        """Test date parsing for ISO format."""
        date_str = "2024-01-01 12:00:00"
        result = news_fetcher._parse_date(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
    
    def test_parse_date_invalid(self, news_fetcher):
        """Test date parsing with invalid format."""
        date_str = "invalid date"
        result = news_fetcher._parse_date(date_str)
        # Should return current time as fallback
        assert isinstance(result, datetime)
    
    def test_extract_content_from_content_field(self, news_fetcher):
        """Test content extraction from content field."""
        entry = {
            'content': [{'value': 'Full article content'}],
            'summary': 'Summary text'
        }
        result = news_fetcher._extract_content(entry)
        assert result == 'Full article content'
    
    def test_extract_content_from_summary(self, news_fetcher):
        """Test content extraction from summary field."""
        entry = {
            'summary': '<p>Summary text</p>',
            'description': 'Description text'
        }
        result = news_fetcher._extract_content(entry)
        # Should extract text from HTML
        assert 'Summary text' in result or result == 'Summary text'
    
    def test_deduplicate_articles(self, news_fetcher):
        """Test article deduplication."""
        articles = [
            {'url': 'https://example.com/article1', 'title': 'Article 1'},
            {'url': 'https://example.com/article2', 'title': 'Article 2'},
            {'url': 'https://example.com/article1', 'title': 'Article 1 Duplicate'},
        ]
        
        unique = news_fetcher.deduplicate_articles(articles)
        assert len(unique) == 2
        assert unique[0]['url'] == 'https://example.com/article1'
        assert unique[1]['url'] == 'https://example.com/article2'
    
    def test_get_active_sources(self, news_fetcher):
        """Test getting active sources."""
        sources = news_fetcher.get_active_sources()
        assert len(sources) > 0
        assert all(source.is_active for source in sources)
    
    @patch('data_sources.news_fetcher.get_all_active_sources')
    @patch.object(NewsFetcher, 'fetch_from_source')
    def test_fetch_all_sources(self, mock_fetch, mock_get_sources, news_fetcher):
        """Test fetching from all sources."""
        # Mock sources
        mock_source1 = Mock()
        mock_source1.name = "source1"
        mock_source2 = Mock()
        mock_source2.name = "source2"
        mock_get_sources.return_value = [mock_source1, mock_source2]
        
        # Mock fetch results
        mock_fetch.side_effect = [
            [{'title': 'Article 1'}],
            [{'title': 'Article 2'}]
        ]
        
        # Fetch all
        articles = news_fetcher.fetch_all_sources(rate_limit=0)
        
        # Verify
        assert len(articles) == 2
        assert mock_fetch.call_count == 2
