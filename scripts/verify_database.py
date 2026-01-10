"""Database verification script."""
import sys
from pathlib import Path
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import get_db, engine
from database.models import Base
from config.settings import settings
from sqlalchemy import inspect, text


def verify_tables():
    """Verify all tables exist."""
    logger.info("Verifying database tables...")
    
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    expected_tables = {
        "stocks", "market_data_daily", "market_data_intraday",
        "screening_signals", "agent_decisions", "orders",
        "trades", "portfolio", "user_actions", "performance_metrics", "tax_ledger",
        "nifty500_sectors", "news_articles", "sentiment_scores",
        "macro_stock_sentiment", "news_sources"
    }
    
    missing_tables = expected_tables - existing_tables
    extra_tables = existing_tables - expected_tables
    
    if missing_tables:
        logger.error(f"❌ Missing tables: {missing_tables}")
        return False
    
    if extra_tables:
        logger.warning(f"⚠️ Extra tables found: {extra_tables}")
    
    logger.info(f"✅ All {len(expected_tables)} required tables exist")
    return True


def verify_schema():
    """Verify table schemas match models."""
    logger.info("Verifying table schemas...")
    
    inspector = inspect(engine)
    issues = []
    
    # Check key tables have required columns
    table_checks = {
        "stocks": ["id", "symbol", "name", "exchange", "sector", "market_cap"],
        "market_data_daily": ["id", "stock_id", "date", "close", "volume"],
        "orders": ["id", "stock_id", "order_type", "order_status"],
        "trades": ["id", "order_id", "entry_price", "quantity"],
    }
    
    for table_name, required_columns in table_checks.items():
        if table_name not in inspector.get_table_names():
            issues.append(f"Table {table_name} does not exist")
            continue
        
        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
        missing_columns = set(required_columns) - existing_columns
        
        if missing_columns:
            issues.append(f"Table {table_name} missing columns: {missing_columns}")
    
    if issues:
        logger.error(f"❌ Schema issues found: {issues}")
        return False
    
    logger.info("✅ Table schemas verified")
    return True


def verify_integrity():
    """Run SQLite integrity check."""
    logger.info("Running database integrity check...")
    
    with get_db() as db:
        result = db.execute(text("PRAGMA integrity_check"))
        integrity_result = result.scalar()
    
    if integrity_result == "ok":
        logger.info("✅ Database integrity check passed")
        return True
    else:
        logger.error(f"❌ Database integrity check failed: {integrity_result}")
        return False


def verify_foreign_keys():
    """Verify foreign key constraints."""
    logger.info("Verifying foreign key constraints...")
    
    with get_db() as db:
        # Enable foreign key checks
        db.execute(text("PRAGMA foreign_keys = ON"))
        
        # Check for orphaned records (basic check)
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM market_data_daily md
                LEFT JOIN stocks s ON md.stock_id = s.id
                WHERE s.id IS NULL
            """)
        )
        orphaned = result.scalar()
        
        if orphaned > 0:
            logger.warning(f"⚠️ Found {orphaned} orphaned records in market_data_daily")
            return False
    
    logger.info("✅ Foreign key constraints verified")
    return True


def get_database_info():
    """Get database information."""
    info = {}
    
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    if db_path.exists():
        info["path"] = str(db_path)
        info["size_mb"] = round(db_path.stat().st_size / (1024 * 1024), 2)
        info["exists"] = True
    else:
        info["exists"] = False
    
    with get_db() as db:
        result = db.execute(text("SELECT sqlite_version()"))
        info["sqlite_version"] = result.scalar()
    
    return info


def main():
    """Main verification function."""
    logger.info("Starting database verification...")
    
    # Get database info
    info = get_database_info()
    logger.info(f"Database info: {info}")
    
    if not info.get("exists"):
        logger.error("❌ Database file does not exist")
        return 1
    
    # Run all checks
    checks = [
        ("Tables", verify_tables),
        ("Schema", verify_schema),
        ("Integrity", verify_integrity),
        ("Foreign Keys", verify_foreign_keys),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        logger.info(f"\n--- {check_name} Check ---")
        if not check_func():
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ All database checks passed")
        return 0
    else:
        logger.error("\n❌ Some database checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
