"""News fetcher for RSS feeds and APIs."""
import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from loguru import logger
from bs4 import BeautifulSoup
import time
from config.news_sources import (
    get_all_active_sources, NewsSourceConfig
)


class NewsFetcher:
    """Fetches news articles from RSS feeds and APIs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_from_source(self, source: NewsSourceConfig) -> List[Dict[str, Any]]:
        """Fetch articles from a single news source."""
        try:
            if source.type == "rss":
                return self._fetch_rss(source)
            elif source.type == "api":
                return self._fetch_api(source)
            else:
                logger.warning(f"Unknown source type: {source.type} for {source.name}")
                return []
        except Exception as e:
            logger.error(f"Error fetching from {source.name}: {e}")
            return []
    
    def _fetch_rss(self, source: NewsSourceConfig) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feed."""
        try:
            # Parse RSS feed
            feed = feedparser.parse(source.url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS parsing error for {source.name}: {feed.bozo_exception}")
                return []
            
            articles = []
            for entry in feed.entries[:50]:  # Limit to 50 most recent
                try:
                    # Parse published date - feedparser provides published_parsed as time tuple
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        # feedparser returns time tuple (9-element struct_time)
                        import calendar
                        # timegm converts UTC time tuple to timestamp (UTC, not local)
                        timestamp = calendar.timegm(entry.published_parsed)
                        # Create UTC datetime then make naive
                        published_date = datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)
                    else:
                        # Fallback to string parsing
                        published_date = self._parse_date(entry.get('published', ''))
                    
                    # Extract article data
                    article = {
                        'source': source.name,
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'published_date': published_date,
                        'summary': entry.get('summary', ''),
                        'content': self._extract_content(entry),
                        'categories': source.categories
                    }
                    
                    # Only add if we have essential fields
                    if article['title'] and article['url']:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Error processing RSS entry for {source.name}: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from {source.name}")
            return articles
            
        except Exception as e:
            logger.error(f"RSS fetch error for {source.name}: {e}")
            return []
    
    def _fetch_api(self, source: NewsSourceConfig) -> List[Dict[str, Any]]:
        """Fetch articles from API endpoint."""
        try:
            # Generic API fetch
            response = self.session.get(
                source.url,
                headers=source.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            # Parse API response based on structure
            # Note: Currently all sources use RSS feeds, so this is a placeholder
            # If adding new API sources, implement parsing here
            articles = []
            return articles
            
        except Exception as e:
            logger.error(f"API fetch error for {source.name}: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object (naive UTC).
        
        Returns:
            Naive datetime in UTC (no timezone info)
        """
        if not date_str:
            from datetime import timezone
            return datetime.now(timezone.utc).replace(tzinfo=None)
        
        try:
            from datetime import timezone
            
            # Try common date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # RSS format with timezone
                '%a, %d %b %Y %H:%M:%S %Z',  # RSS format with timezone name
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d-%m-%Y',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # If timezone-aware, convert to UTC and make naive
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    return dt
                except ValueError:
                    continue
            
            # If all formats fail, try feedparser's date parser
            import feedparser
            parsed = feedparser._parse_date(date_str)
            if parsed:
                # feedparser returns timezone-aware tuple, convert to naive UTC
                dt = datetime.fromtimestamp(time.mktime(parsed))
                # If parsed date has timezone info, handle it
                # feedparser._parse_date returns a time tuple, mktime assumes local time
                # For RSS feeds, we'll treat as UTC if no timezone specified
                return dt
            
            # Fallback to current time (naive UTC)
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.now(timezone.utc).replace(tzinfo=None)
            
        except Exception as e:
            logger.warning(f"Date parsing error: {e}")
            from datetime import timezone
            return datetime.now(timezone.utc).replace(tzinfo=None)
    
    def _extract_content(self, entry: Dict) -> str:
        """Extract full content from RSS entry."""
        # Try to get content from various fields
        content = entry.get('content', [])
        if content and isinstance(content, list) and len(content) > 0:
            return content[0].get('value', '')
        
        # Fallback to summary
        summary = entry.get('summary', '')
        if summary:
            # Try to extract text from HTML
            try:
                soup = BeautifulSoup(summary, 'html.parser')
                return soup.get_text()
            except:
                return summary
        
        return entry.get('description', '')
    
    def fetch_all_sources(self, rate_limit: float = 1.0) -> List[Dict[str, Any]]:
        """Fetch articles from all active sources with rate limiting."""
        sources = get_all_active_sources()
        all_articles = []
        
        for source in sources:
            try:
                articles = self.fetch_from_source(source)
                all_articles.extend(articles)
                
                # Rate limiting
                if rate_limit > 0:
                    time.sleep(rate_limit)
                    
            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {e}")
                continue
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        logger.info(f"Deduplicated: {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles
    
    def get_active_sources(self) -> List[NewsSourceConfig]:
        """Get list of active news sources."""
        return get_all_active_sources()
