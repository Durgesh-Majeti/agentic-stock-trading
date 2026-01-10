"""Update news sources in database with all active sources from config."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import get_db
from database.models import NewsSource
from config.news_sources import get_all_active_sources
from loguru import logger
from config.logging_config import setup_logging


def update_news_sources():
    """Add missing news sources to database."""
    setup_logging()
    
    logger.info("Updating news sources in database...")
    
    active_sources = get_all_active_sources()
    logger.info(f"Found {len(active_sources)} active sources in config")
    
    with get_db() as session:
        added_count = 0
        updated_count = 0
        
        for source_config in active_sources:
            # Check if source exists
            existing = session.query(NewsSource).filter(
                NewsSource.name == source_config.name
            ).first()
            
            if existing:
                # Update existing source
                existing.url_pattern = source_config.url
                existing.fetch_frequency = source_config.fetch_frequency
                existing.is_active = source_config.is_active
                updated_count += 1
                logger.debug(f"Updated: {source_config.name}")
            else:
                # Add new source
                news_source = NewsSource(
                    name=source_config.name,
                    url_pattern=source_config.url,
                    fetch_frequency=source_config.fetch_frequency,
                    is_active=source_config.is_active
                )
                session.add(news_source)
                added_count += 1
                logger.info(f"Added: {source_config.name}")
        
        session.commit()
        logger.info(f"✅ Added {added_count} new sources, updated {updated_count} existing sources")
        
        # Verify
        total_sources = session.query(NewsSource).count()
        logger.info(f"Total news sources in database: {total_sources}")
        
        return True


if __name__ == "__main__":
    logger.info("Starting news sources update...")
    success = update_news_sources()
    if success:
        logger.info("✅ Update completed successfully")
    else:
        logger.error("❌ Update failed")
        exit(1)
