"""Database migration script to add sentiment analysis tables."""
import sys
import sqlite3
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.settings import settings


def migrate_add_sentiment_tables():
    """Add sentiment analysis tables to database."""
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        logger.info("Adding sentiment analysis tables...")
        
        # Create news_articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                published_date DATETIME NOT NULL,
                category TEXT,
                relevance_score REAL,
                is_macro BOOLEAN DEFAULT 0,
                macro_category TEXT,
                affected_sectors TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_id) REFERENCES stocks(id)
            )
        """)
        
        # Create indexes for news_articles
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_stock 
            ON news_articles(stock_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_date 
            ON news_articles(published_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_category 
            ON news_articles(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_relevance 
            ON news_articles(relevance_score)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_macro 
            ON news_articles(is_macro, macro_category)
        """)
        
        # Create sentiment_scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER,
                date DATE NOT NULL,
                overall_sentiment REAL NOT NULL,
                confidence REAL NOT NULL,
                article_count INTEGER DEFAULT 0,
                positive_count INTEGER DEFAULT 0,
                negative_count INTEGER DEFAULT 0,
                neutral_count INTEGER DEFAULT 0,
                stock_specific_sentiment REAL,
                sector_sentiment REAL,
                macro_sentiment REAL,
                government_sentiment REAL,
                international_sentiment REAL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_id) REFERENCES stocks(id),
                UNIQUE(stock_id, date)
            )
        """)
        
        # Create indexes for sentiment_scores
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_stock_date 
            ON sentiment_scores(stock_id, date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_date 
            ON sentiment_scores(date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_overall 
            ON sentiment_scores(overall_sentiment)
        """)
        
        # Create macro_stock_sentiment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_stock_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_article_id INTEGER NOT NULL,
                stock_id INTEGER NOT NULL,
                macro_sentiment REAL NOT NULL,
                sector_impact REAL NOT NULL,
                stock_sentiment REAL NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_article_id) REFERENCES news_articles(id),
                FOREIGN KEY (stock_id) REFERENCES stocks(id)
            )
        """)
        
        # Create indexes for macro_stock_sentiment
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macro_stock 
            ON macro_stock_sentiment(stock_id, created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macro_news 
            ON macro_stock_sentiment(news_article_id)
        """)
        
        # Create news_sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url_pattern TEXT NOT NULL,
                api_key TEXT,
                is_active BOOLEAN DEFAULT 1,
                fetch_frequency INTEGER DEFAULT 15,
                last_fetched DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default news sources
        default_sources = [
            ("economic_times_markets", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", 15),
            ("economic_times_economy", "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms", 15),
            ("moneycontrol_latest", "https://www.moneycontrol.com/rss/latestnews.xml", 15),
            ("business_standard_markets", "https://www.business-standard.com/rss/markets-106.rss", 15),
        ]
        
        for name, url, freq in default_sources:
            cursor.execute("""
                INSERT OR IGNORE INTO news_sources (name, url_pattern, fetch_frequency, is_active)
                VALUES (?, ?, ?, 1)
            """, (name, url, freq))
        
        conn.commit()
        logger.info("✅ Sentiment analysis tables created successfully")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%news%' OR name LIKE '%sentiment%'")
        tables = cursor.fetchall()
        logger.info(f"Created tables: {[t[0] for t in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    logger.info("Starting sentiment analysis tables migration...")
    success = migrate_add_sentiment_tables()
    if success:
        logger.info("✅ Migration completed successfully")
    else:
        logger.error("❌ Migration failed")
        exit(1)
