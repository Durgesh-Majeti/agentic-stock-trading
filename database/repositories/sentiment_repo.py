"""Sentiment repository for news articles and sentiment scores."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, date, timedelta, timezone
from database.models import (
    NewsArticle, SentimentScore, MacroStockSentiment, 
    NewsSource, Stock
)
from loguru import logger


class SentimentRepository:
    """Repository for sentiment and news article operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # News Article Operations
    
    def store_article(
        self,
        source: str,
        title: str,
        content: str,
        url: str,
        published_date: datetime,
        stock_id: Optional[int] = None,
        category: Optional[str] = None,
        relevance_score: Optional[float] = None,
        is_macro: bool = False,
        macro_category: Optional[str] = None,
        affected_sectors: Optional[str] = None
    ) -> NewsArticle:
        """Store a news article."""
        # Check if article already exists
        existing = self.session.query(NewsArticle).filter(
            NewsArticle.url == url
        ).first()
        
        if existing:
            # Update existing article
            existing.title = title
            existing.content = content
            existing.stock_id = stock_id
            existing.category = category
            existing.relevance_score = relevance_score
            existing.is_macro = is_macro
            existing.macro_category = macro_category
            existing.affected_sectors = affected_sectors
            self.session.commit()
            self.session.refresh(existing)
            return existing
        
        # Create new article
        article = NewsArticle(
            stock_id=stock_id,
            source=source,
            title=title,
            content=content,
            url=url,
            published_date=published_date,
            category=category,
            relevance_score=relevance_score,
            is_macro=is_macro,
            macro_category=macro_category,
            affected_sectors=affected_sectors
        )
        self.session.add(article)
        self.session.commit()
        self.session.refresh(article)
        return article
    
    def get_articles_for_stock(
        self,
        stock_id: int,
        date_filter: Optional[date] = None,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Get articles for a specific stock."""
        query = self.session.query(NewsArticle).filter(
            NewsArticle.stock_id == stock_id
        )
        
        if date_filter:
            query = query.filter(
                func.date(NewsArticle.published_date) == date_filter
            )
        
        return query.order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def get_sector_articles(
        self,
        sector: str,
        date_filter: Optional[date] = None,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Get articles for a specific sector."""
        query = self.session.query(NewsArticle).join(Stock).filter(
            Stock.sector == sector,
            NewsArticle.category.in_(['sector', 'stock_specific'])
        )
        
        if date_filter:
            query = query.filter(
                func.date(NewsArticle.published_date) == date_filter
            )
        
        return query.order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def get_macro_articles(
        self,
        date_filter: Optional[date] = None,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Get macro-level articles."""
        query = self.session.query(NewsArticle).filter(
            NewsArticle.is_macro == True
        )
        
        if date_filter:
            query = query.filter(
                func.date(NewsArticle.published_date) == date_filter
            )
        
        return query.order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def get_recent_articles(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Get recent articles within specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.session.query(NewsArticle).filter(
            NewsArticle.published_date >= cutoff
        ).order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def cleanup_old_articles(self, days: int = 30) -> int:
        """Delete articles older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.session.query(NewsArticle).filter(
            NewsArticle.published_date < cutoff
        ).delete()
        self.session.commit()
        return deleted
    
    # Sentiment Score Operations
    
    def store_daily_sentiment(
        self,
        stock_id: Optional[int],
        sentiment_date: date,
        overall_sentiment: float,
        confidence: float,
        article_count: int = 0,
        positive_count: int = 0,
        negative_count: int = 0,
        neutral_count: int = 0,
        stock_specific_sentiment: Optional[float] = None,
        sector_sentiment: Optional[float] = None,
        macro_sentiment: Optional[float] = None,
        government_sentiment: Optional[float] = None,
        international_sentiment: Optional[float] = None
    ) -> SentimentScore:
        """Store or update daily sentiment score."""
        # Check if sentiment already exists for this date
        existing = self.session.query(SentimentScore).filter(
            and_(
                SentimentScore.stock_id == stock_id,
                SentimentScore.date == sentiment_date
            )
        ).first()
        
        if existing:
            # Update existing sentiment
            existing.overall_sentiment = overall_sentiment
            existing.confidence = confidence
            existing.article_count = article_count
            existing.positive_count = positive_count
            existing.negative_count = negative_count
            existing.neutral_count = neutral_count
            existing.stock_specific_sentiment = stock_specific_sentiment
            existing.sector_sentiment = sector_sentiment
            existing.macro_sentiment = macro_sentiment
            existing.government_sentiment = government_sentiment
            existing.international_sentiment = international_sentiment
            self.session.commit()
            self.session.refresh(existing)
            return existing
        
        # Create new sentiment score
        sentiment = SentimentScore(
            stock_id=stock_id,
            date=sentiment_date,
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            article_count=article_count,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            stock_specific_sentiment=stock_specific_sentiment,
            sector_sentiment=sector_sentiment,
            macro_sentiment=macro_sentiment,
            government_sentiment=government_sentiment,
            international_sentiment=international_sentiment
        )
        self.session.add(sentiment)
        self.session.commit()
        self.session.refresh(sentiment)
        return sentiment
    
    def get_sentiment_for_stock(
        self,
        stock_id: int,
        sentiment_date: Optional[date] = None
    ) -> Optional[SentimentScore]:
        """Get sentiment score for a stock."""
        query = self.session.query(SentimentScore).filter(
            SentimentScore.stock_id == stock_id
        )
        
        if sentiment_date:
            query = query.filter(SentimentScore.date == sentiment_date)
        else:
            # Get latest sentiment
            query = query.order_by(desc(SentimentScore.date))
        
        return query.first()
    
    def get_macro_sentiment_for_stock(
        self,
        stock_id: int,
        sentiment_date: Optional[date] = None
    ) -> float:
        """Get macro sentiment propagated to a stock."""
        query = self.session.query(MacroStockSentiment).filter(
            MacroStockSentiment.stock_id == stock_id
        )
        
        if sentiment_date:
            query = query.filter(
                func.date(MacroStockSentiment.created_at) == sentiment_date
            )
        
        # Get average macro sentiment for the stock
        result = query.with_entities(
            func.avg(MacroStockSentiment.stock_sentiment)
        ).scalar()
        
        return result if result else 0.0
    
    # Macro Stock Sentiment Operations
    
    def store_macro_sentiment_mappings(
        self,
        mappings: List[Dict[str, Any]]
    ) -> List[MacroStockSentiment]:
        """Store macro-to-stock sentiment mappings."""
        stored = []
        for mapping in mappings:
            macro_sentiment = MacroStockSentiment(
                news_article_id=mapping['news_article_id'],
                stock_id=mapping['stock_id'],
                macro_sentiment=mapping['macro_sentiment'],
                sector_impact=mapping['sector_impact'],
                stock_sentiment=mapping['stock_sentiment']
            )
            self.session.add(macro_sentiment)
            stored.append(macro_sentiment)
        
        self.session.commit()
        for item in stored:
            self.session.refresh(item)
        return stored
    
    def cleanup_old_macro_mappings(self, days: int = 90) -> int:
        """Delete macro sentiment mappings older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.session.query(MacroStockSentiment).filter(
            MacroStockSentiment.created_at < cutoff
        ).delete()
        self.session.commit()
        return deleted
    
    # News Source Operations
    
    def get_active_sources(self) -> List[NewsSource]:
        """Get all active news sources."""
        return self.session.query(NewsSource).filter(
            NewsSource.is_active == True
        ).all()
    
    def get_source_last_fetched(self, source_name: str) -> Optional[datetime]:
        """Get last fetched timestamp for a source.
        
        Args:
            source_name: Name of the news source
        
        Returns:
            Last fetched datetime or None if never fetched
        """
        source = self.session.query(NewsSource).filter(
            NewsSource.name == source_name
        ).first()
        
        return source.last_fetched if source else None
    
    def get_latest_article_date_for_source(self, source_name: str) -> Optional[datetime]:
        """Get the latest article published date for a specific source.
        
        Args:
            source_name: Name of the news source
        
        Returns:
            Latest article published date or None if no articles
        """
        try:
            result = self.session.query(func.max(NewsArticle.published_date)).filter(
                NewsArticle.source == source_name
            ).scalar()
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting latest article date for {source_name}: {e}")
            return None
    
    def get_latest_article_date(self, source: Optional[str] = None) -> Optional[datetime]:
        """Get the latest article published date from database (all sources or specific source).
        
        Args:
            source: Optional source name to filter by
        
        Returns:
            Latest article published date or None if no articles
        """
        try:
            query = self.session.query(func.max(NewsArticle.published_date))
            if source:
                query = query.filter(NewsArticle.source == source)
            
            result = query.scalar()
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting latest article date: {e}")
            return None
    
    def get_source_status(self, source_name: str) -> Dict[str, Any]:
        """Get status information for a news source.
        
        Args:
            source_name: Name of the news source
        
        Returns:
            Dictionary with status information:
            - last_fetched: Last fetch timestamp
            - latest_article_date: Latest article published date
            - article_count: Total number of articles from this source
            - last_24h_count: Articles in last 24 hours
        """
        source = self.session.query(NewsSource).filter(
            NewsSource.name == source_name
        ).first()
        
        if not source:
            return {
                'source_name': source_name,
                'exists': False,
                'last_fetched': None,
                'latest_article_date': None,
                'article_count': 0,
                'last_24h_count': 0
            }
        
        latest_article_date = self.get_latest_article_date_for_source(source_name)
        
        # Count total articles
        total_count = self.session.query(func.count(NewsArticle.id)).filter(
            NewsArticle.source == source_name
        ).scalar() or 0
        
        # Count articles in last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        last_24h_count = self.session.query(func.count(NewsArticle.id)).filter(
            NewsArticle.source == source_name,
            NewsArticle.published_date >= cutoff
        ).scalar() or 0
        
        return {
            'source_name': source_name,
            'exists': True,
            'is_active': source.is_active,
            'last_fetched': source.last_fetched,
            'latest_article_date': latest_article_date,
            'article_count': total_count,
            'last_24h_count': last_24h_count,
            'fetch_frequency': source.fetch_frequency
        }
    
    def get_all_sources_status(self) -> List[Dict[str, Any]]:
        """Get status information for all news sources.
        
        Returns:
            List of status dictionaries for all sources
        """
        sources = self.get_active_sources()
        return [self.get_source_status(source.name) for source in sources]
    
    def get_source_fetch_start_date(
        self, 
        source_name: str, 
        default_days: int = 30
    ) -> datetime:
        """Get the start date for fetching articles from a source.
        
        Uses the most recent of:
        1. Source's last_fetched timestamp
        2. Latest article published_date for that source
        3. Default days ago (if no history)
        
        Args:
            source_name: Name of the news source
            default_days: Default days to go back if no history
        
        Returns:
            Start date for fetching
        """
        # Check source's last_fetched
        source_last_fetched = self.get_source_last_fetched(source_name)
        
        # Check latest article date for this source
        latest_article_date = self.get_latest_article_date_for_source(source_name)
        
        # Use the most recent timestamp
        if source_last_fetched and latest_article_date:
            # Use the more recent one (but subtract 1 hour buffer for safety)
            most_recent = max(source_last_fetched, latest_article_date)
            return most_recent - timedelta(hours=1)  # 1 hour buffer
        elif source_last_fetched:
            return source_last_fetched - timedelta(hours=1)
        elif latest_article_date:
            return latest_article_date - timedelta(hours=1)
        else:
            # No history: use default days
            return datetime.now() - timedelta(days=default_days)
    
    def update_source_last_fetched(
        self,
        source_name: str,
        last_fetched: datetime
    ) -> None:
        """Update last fetched timestamp for a source."""
        source = self.session.query(NewsSource).filter(
            NewsSource.name == source_name
        ).first()
        
        if source:
            source.last_fetched = last_fetched
            self.session.commit()
        else:
            logger.warning(f"Source {source_name} not found in database")
    
    def get_stock_sector(self, stock_id: int) -> Optional[str]:
        """Get sector for a stock."""
        stock = self.session.query(Stock).filter(
            Stock.id == stock_id
        ).first()
        return stock.sector if stock else None
    
    def get_all_stocks_with_sectors(self) -> List[Dict[str, Any]]:
        """Get all stocks with their sectors and metadata."""
        stocks = self.session.query(Stock).filter(
            Stock.is_active == True
        ).all()
        
        return [
            {
                'id': stock.id,
                'symbol': stock.symbol,
                'sector': stock.sector,
                'market_cap': stock.market_cap,
                'beta': 1.0  # Default beta, should be added to Stock model if needed
            }
            for stock in stocks
        ]
    
    def get_existing_urls(self, since_date: Optional[datetime] = None) -> Set[str]:
        """Get set of existing article URLs (optimized for bulk checking).
        
        Args:
            since_date: Only check URLs from articles published after this date
        
        Returns:
            Set of existing URLs
        """
        try:
            query = self.session.query(NewsArticle.url)
            if since_date:
                query = query.filter(NewsArticle.published_date >= since_date)
            
            urls = {row[0] for row in query.all()}
            return urls
        except Exception as e:
            logger.error(f"Error getting existing URLs: {e}")
            return set()
    
    def bulk_store_articles(
        self,
        articles: List[Dict[str, Any]],
        existing_urls: Optional[Set[str]] = None,
        force_refresh: bool = False
    ) -> tuple[int, int]:
        """Bulk store articles with optimized insert/update logic.
        
        Args:
            articles: List of article dictionaries
            existing_urls: Set of existing URLs (if None, will query database)
            force_refresh: If True, update existing articles instead of skipping
        
        Returns:
            (inserted_count, updated_count)
        """
        if not articles:
            return 0, 0
        
        # Get existing URLs if not provided
        if existing_urls is None:
            existing_urls = self.get_existing_urls()
        
        # Separate into insert and update
        to_insert = []
        to_update = []
        
        # Get all existing articles in one query (optimization)
        if existing_urls:
            existing_articles = {
                art.url: art 
                for art in self.session.query(NewsArticle).filter(
                    NewsArticle.url.in_(existing_urls)
                ).all()
            }
        else:
            existing_articles = {}
        
        for article in articles:
            url = article.get('url', '')
            if not url:
                continue
            
            if url in existing_urls:
                # Article exists - update if force_refresh
                if force_refresh and url in existing_articles:
                    existing = existing_articles[url]
                    # Update existing
                    existing.title = article.get('title', existing.title)
                    existing.content = article.get('content', article.get('summary', existing.content))
                    existing.published_date = article.get('published_date', existing.published_date)
                    if article.get('categories'):
                        existing.category = article.get('categories', [None])[0]
                    to_update.append(existing)
                # If not force_refresh, skip (already exists)
            else:
                # New article
                to_insert.append(NewsArticle(
                    source=article.get('source', ''),
                    title=article.get('title', ''),
                    content=article.get('content', article.get('summary', '')),
                    url=url,
                    published_date=article.get('published_date', datetime.now()),
                    category=article.get('categories', [None])[0] if article.get('categories') else None
                ))
        
        # Bulk insert new articles
        inserted = 0
        if to_insert:
            try:
                self.session.bulk_save_objects(to_insert)
                inserted = len(to_insert)
            except Exception as e:
                logger.error(f"Error in bulk insert: {e}")
                # Fallback to individual inserts
                for article_obj in to_insert:
                    try:
                        self.session.add(article_obj)
                        inserted += 1
                    except Exception as e2:
                        logger.warning(f"Error inserting article {article_obj.url}: {e2}")
        
        # Updates are already tracked by SQLAlchemy (objects are modified in place)
        updated = len(to_update)
        
        # Commit all changes
        try:
            self.session.commit()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.session.rollback()
            raise
        
        return inserted, updated
