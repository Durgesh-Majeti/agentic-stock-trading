"""Database maintenance script."""
import sys
from pathlib import Path
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import get_db
from config.settings import settings
from config.constants import DAILY_DATA_RETENTION_DAYS, INTRADAY_DATA_RETENTION_DAYS
from datetime import date, timedelta
from sqlalchemy import text


def vacuum_database():
    """Run VACUUM on SQLite database to reclaim space."""
    logger.info("Running VACUUM on database...")
    
    with get_db() as db:
        db.execute(text("VACUUM"))
        db.commit()
    
    logger.info("✅ VACUUM completed")


def analyze_database():
    """Run ANALYZE on database to update statistics."""
    logger.info("Running ANALYZE on database...")
    
    with get_db() as db:
        db.execute(text("ANALYZE"))
        db.commit()
    
    logger.info("✅ ANALYZE completed")


def cleanup_old_data():
    """Remove old data based on retention policies."""
    logger.info("Cleaning up old data...")
    
    cutoff_daily = date.today() - timedelta(days=DAILY_DATA_RETENTION_DAYS)
    cutoff_intraday = date.today() - timedelta(days=INTRADAY_DATA_RETENTION_DAYS)
    
    with get_db() as db:
        # Clean up old daily data
        result_daily = db.execute(
            text("DELETE FROM market_data_daily WHERE date < :cutoff"),
            {"cutoff": cutoff_daily}
        )
        deleted_daily = result_daily.rowcount
        
        # Clean up old intraday data
        result_intraday = db.execute(
            text("DELETE FROM market_data_intraday WHERE date < :cutoff"),
            {"cutoff": cutoff_intraday}
        )
        deleted_intraday = result_intraday.rowcount
        
        db.commit()
    
    logger.info(f"✅ Cleaned up {deleted_daily} daily records and {deleted_intraday} intraday records")
    return deleted_daily + deleted_intraday


def get_database_stats():
    """Get database statistics."""
    stats = {}
    
    with get_db() as db:
        # Get table sizes
        tables = [
            "stocks", "market_data_daily", "market_data_intraday",
            "screening_signals", "agent_decisions", "orders",
            "trades", "portfolio", "user_actions", "performance_metrics", "tax_ledger"
        ]
        
        for table in tables:
            result = db.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )
            stats[table] = result.scalar()
        
        # Get database file size
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if db_path.exists():
            stats["file_size_mb"] = round(db_path.stat().st_size / (1024 * 1024), 2)
    
    return stats


def main():
    """Main maintenance function."""
    try:
        logger.info("Starting database maintenance...")
        
        # Get stats before
        stats_before = get_database_stats()
        logger.info(f"Database stats before: {stats_before}")
        
        # Run maintenance tasks
        cleanup_old_data()
        analyze_database()
        vacuum_database()
        
        # Get stats after
        stats_after = get_database_stats()
        logger.info(f"Database stats after: {stats_after}")
        
        logger.info("✅ Database maintenance completed")
        return 0
    except Exception as e:
        logger.error(f"❌ Database maintenance failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
