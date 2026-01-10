"""Sentiment repository for news articles and sentiment scores."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from database.models import (
    NewsArticle, SentimentScore, MacroStockSentiment, 
    NewsSource, Stock
)


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
