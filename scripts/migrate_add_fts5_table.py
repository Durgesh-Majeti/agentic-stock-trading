"""Database migration script to add FTS5 full-text search virtual table for news articles."""
import sys
import sqlite3
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.settings import settings


def migrate_add_fts5_table():
    """Add FTS5 virtual table for news articles full-text search."""
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        logger.info("Adding FTS5 virtual table for news articles...")
        
        # Check if news_articles table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='news_articles'
        """)
        if not cursor.fetchone():
            logger.error("news_articles table does not exist. Run migrate_add_sentiment_tables.py first.")
            conn.close()
            return False
        
        # Check if FTS5 table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='news_articles_fts'
        """)
        if cursor.fetchone():
            logger.info("news_articles_fts table already exists. Skipping creation.")
            conn.close()
            return True
        
        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE news_articles_fts USING fts5(
                title,
                content,
                content='news_articles',
                content_rowid='id'
            )
        """)
        
        # Populate FTS5 table with existing data
        cursor.execute("""
            INSERT INTO news_articles_fts(rowid, title, content)
            SELECT id, title, content FROM news_articles
        """)
        
        # Create triggers to keep FTS5 table in sync with news_articles
        # Trigger for INSERT
        cursor.execute("""
            CREATE TRIGGER news_articles_fts_insert AFTER INSERT ON news_articles BEGIN
                INSERT INTO news_articles_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)
        
        # Trigger for UPDATE
        cursor.execute("""
            CREATE TRIGGER news_articles_fts_update AFTER UPDATE ON news_articles BEGIN
                UPDATE news_articles_fts SET
                    title = new.title,
                    content = new.content
                WHERE rowid = new.id;
            END
        """)
        
        # Trigger for DELETE
        cursor.execute("""
            CREATE TRIGGER news_articles_fts_delete AFTER DELETE ON news_articles BEGIN
                DELETE FROM news_articles_fts WHERE rowid = old.id;
            END
        """)
        
        conn.commit()
        logger.info("✅ FTS5 virtual table and triggers created successfully")
        
        # Verify creation
        cursor.execute("SELECT COUNT(*) FROM news_articles_fts")
        count = cursor.fetchone()[0]
        logger.info(f"FTS5 table populated with {count} articles")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    logger.info("Starting FTS5 virtual table migration...")
    success = migrate_add_fts5_table()
    if success:
        logger.info("✅ Migration completed successfully")
    else:
        logger.error("❌ Migration failed")
        exit(1)
