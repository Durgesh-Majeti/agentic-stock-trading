"""Initialize database - create all tables."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import init_db
from loguru import logger


def main():
    """Initialize database."""
    try:
        logger.info("Starting database initialization...")
        init_db()
        logger.info("✅ Database initialized successfully!")
        return 0
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
