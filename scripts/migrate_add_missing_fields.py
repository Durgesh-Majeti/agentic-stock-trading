"""Database migration script to add missing fields to existing tables."""
import sys
import sqlite3
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.settings import settings


def migrate_add_missing_fields():
    """Add missing fields to existing tables."""
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        logger.info("Adding missing fields to existing tables...")
        
        # Check and add broker_order_id to orders table
        cursor.execute("PRAGMA table_info(orders)")
        order_columns = [row[1] for row in cursor.fetchall()]
        
        if 'broker_order_id' not in order_columns:
            logger.info("Adding 'broker_order_id' column to orders table...")
            cursor.execute("ALTER TABLE orders ADD COLUMN broker_order_id TEXT")
            logger.info("✅ Added broker_order_id to orders")
        else:
            logger.info("broker_order_id already exists in orders table")
        
        # Check and add missing indicators to market_data_daily
        cursor.execute("PRAGMA table_info(market_data_daily)")
        daily_columns = [row[1] for row in cursor.fetchall()]
        
        missing_indicators = []
        if 'mfi' not in daily_columns:
            missing_indicators.append('mfi')
        if 'ema_20' not in daily_columns:
            missing_indicators.append('ema_20')
        if 'ema_50' not in daily_columns:
            missing_indicators.append('ema_50')
        
        for indicator in missing_indicators:
            logger.info(f"Adding '{indicator}' column to market_data_daily table...")
            cursor.execute(f"ALTER TABLE market_data_daily ADD COLUMN {indicator} REAL")
            logger.info(f"✅ Added {indicator} to market_data_daily")
        
        if not missing_indicators:
            logger.info("All indicators already exist in market_data_daily table")
        
        # Create nifty500_sectors table if it doesn't exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='nifty500_sectors'
        """)
        if not cursor.fetchone():
            logger.info("Creating nifty500_sectors table...")
            cursor.execute("""
                CREATE TABLE nifty500_sectors (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT,
                    industry TEXT,
                    market_cap_rank INTEGER
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sectors_sector ON nifty500_sectors(sector)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sectors_industry ON nifty500_sectors(industry)")
            logger.info("✅ Created nifty500_sectors table")
        else:
            logger.info("nifty500_sectors table already exists")
        
        conn.commit()
        logger.info("✅ Migration completed successfully")
        
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
    logger.info("Starting missing fields migration...")
    success = migrate_add_missing_fields()
    if success:
        logger.info("✅ Migration completed successfully")
    else:
        logger.error("❌ Migration failed")
        exit(1)
