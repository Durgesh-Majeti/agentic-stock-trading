"""Fetch and store news articles with optimized incremental updates."""
import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional, Set
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.news_fetcher import NewsFetcher
from database.repositories.sentiment_repo import SentimentRepository
from database.session import get_db
from database.models import NewsArticle
from sqlalchemy import func
from loguru import logger
from config.logging_config import setup_logging

# Global counters
stored_count = 0
skipped_count = 0
error_count = 0


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime to naive UTC.
    
    If timezone-aware, converts to UTC then removes timezone info.
    If already naive, returns as-is (assumed to be UTC).
    
    Args:
        dt: Datetime object (naive or timezone-aware)
    
    Returns:
        Naive datetime in UTC
    """
    if dt is None:
        return None
    
    # If timezone-aware, convert to UTC then make naive
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    return dt


def filter_articles_by_date(
    articles: List[Dict[str, Any]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Filter articles by date range."""
    if not start_date and not end_date:
        return articles
    
    filtered = []
    for article in articles:
        pub_date = article.get('published_date')
        if not pub_date:
            continue
        
        if start_date and pub_date < start_date:
            continue
        if end_date and pub_date > end_date:
            continue
        
        filtered.append(article)
    
    return filtered


def store_articles_bulk(
    repo: SentimentRepository,
    articles: List[Dict[str, Any]],
    existing_urls: Set[str],
    force_refresh: bool = False
) -> tuple[int, int, int]:
    """Store articles in bulk with optimized insert/update logic.
    
    Returns:
        (stored_count, updated_count, skipped_count)
    """
    if not articles:
        return 0, 0, 0
    
    # Filter out articles without URLs
    valid_articles = [a for a in articles if a.get('url')]
    skipped = len(articles) - len(valid_articles)
    
    # Use bulk_store_articles which handles both insert and update
    inserted, updated = repo.bulk_store_articles(
        valid_articles, 
        existing_urls, 
        force_refresh=force_refresh
    )
    
    # Calculate skipped (articles that exist and we're not updating)
    if not force_refresh:
        skipped += len([a for a in valid_articles if a.get('url') in existing_urls])
    
    return inserted, updated, skipped


def fetch_and_store_news(
    session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    force_refresh: bool = False,
    update_recent_days: Optional[int] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Fetch and store news articles with optimized logic.
    
    Args:
        session: Database session
        start_date: Start date for articles (default: latest article date or 30 days ago)
        end_date: End date for articles (default: now)
        force_refresh: If True, re-fetch and update all articles
        update_recent_days: If specified, only fetch last N days
        sources: List of source names to fetch (None = all active sources)
    
    Returns:
        Dictionary with statistics
    """
    global stored_count, skipped_count, error_count
    
    logger.info("=" * 60)
    logger.info("News Fetch and Store Process")
    logger.info("=" * 60)
    
    # Set default dates (normalize to naive UTC)
    if end_date is None:
        end_date = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        # Normalize end_date if provided
        end_date = normalize_datetime(end_date)
    
    # Initialize fetcher and repository
    fetcher = NewsFetcher()
    repo = SentimentRepository(session)
    
    # Log current source statuses (for monitoring)
    logger.info("Current source statuses:")
    source_statuses = repo.get_all_sources_status()
    for status in source_statuses:
        if status['exists']:
            last_fetch_str = status['last_fetched'].strftime('%Y-%m-%d %H:%M:%S') if status['last_fetched'] else 'Never'
            latest_article_str = status['latest_article_date'].strftime('%Y-%m-%d %H:%M:%S') if status['latest_article_date'] else 'None'
            logger.info(f"  {status['source_name']}: Last fetched={last_fetch_str}, Latest article={latest_article_str}, Count={status['article_count']}")
    
    # Get active sources first (needed for per-source date calculation
    all_sources = fetcher.get_active_sources()
    if sources:
        # Filter to specified sources
        sources_to_fetch = [s for s in all_sources if s.name in sources]
        logger.info(f"Fetching from {len(sources_to_fetch)} specified sources")
    else:
        sources_to_fetch = all_sources
        logger.info(f"Fetching from {len(sources_to_fetch)} active sources")
    
    # Determine start_date if not provided
    # For per-source fetching, we'll calculate per source, but set a global minimum
    if start_date is None:
        if update_recent_days is not None:
            # update_recent_days overrides everything
            start_date = end_date - timedelta(days=update_recent_days)
            logger.info(f"Update recent days mode: Fetching last {update_recent_days} days")
        elif not force_refresh:
            # Incremental mode: get earliest start date across all sources
            source_start_dates = []
            for source in sources_to_fetch:
                source_start = repo.get_source_fetch_start_date(source.name, default_days=30)
                source_start_dates.append(source_start)
                logger.debug(f"{source.name}: Start date = {source_start}")
            
            if source_start_dates:
                # Use the earliest date (most conservative)
                start_date = min(source_start_dates)
                logger.info(f"Incremental mode: Earliest source start date = {start_date}")
            else:
                # No sources: fetch last 30 days
                start_date = end_date - timedelta(days=30)
                logger.info(f"No sources configured: Fetching last 30 days")
        else:
            # Force refresh: fetch last 30 days
            start_date = end_date - timedelta(days=30)
            logger.info(f"Force refresh mode: Fetching last 30 days")
    
    # Normalize start_date to naive UTC
    if start_date:
        start_date = normalize_datetime(start_date)
    
    logger.info(f"Global date range: {start_date} to {end_date}")
    
    # Get existing URLs (optimization: only check recent if not force_refresh)
    logger.info("Checking existing articles in database...")
    since_date = None
    if not force_refresh:
        # For incremental mode, only check URLs from last 30 days
        since_date = datetime.now() - timedelta(days=30)
    
    existing_urls = repo.get_existing_urls(since_date=since_date)
    logger.info(f"Found {len(existing_urls)} existing articles in database")
    
    # Fetch articles from all sources
    all_articles = []
    source_stats = {}
    
    for source in sources_to_fetch:
        try:
            # Determine per-source start date (for incremental mode)
            if not force_refresh and update_recent_days is None:
                # Use source-specific start date (more efficient)
                source_start_date = repo.get_source_fetch_start_date(source.name, default_days=30)
                logger.info(f"Fetching from {source.name} (since {source_start_date})...")
            else:
                # Use global start_date for force_refresh or update_recent_days
                source_start_date = start_date
                logger.info(f"Fetching from {source.name} (date range: {source_start_date} to {end_date})...")
            
            articles = fetcher.fetch_from_source(source)
            
            # Filter by date range (per-source or global)
            filtered = filter_articles_by_date(articles, source_start_date, end_date)
            
            # Deduplicate within source
            unique_in_source = fetcher.deduplicate_articles(filtered)
            
            all_articles.extend(unique_in_source)
            source_stats[source.name] = len(unique_in_source)
            logger.info(f"  {source.name}: {len(unique_in_source)} articles (after date filter)")
            
            # Update source last_fetched immediately after successful fetch
            # This ensures we track progress even if storage fails
            # Use current UTC time for consistency
            fetch_timestamp = datetime.now()
            try:
                repo.update_source_last_fetched(source.name, fetch_timestamp)
                logger.debug(f"  Updated {source.name} last_fetched to {fetch_timestamp}")
            except Exception as e:
                logger.warning(f"Error updating last_fetched for {source.name}: {e}")
            
            # Rate limiting between sources
            time.sleep(1.0)  # 1 second delay between sources
            
        except Exception as e:
            logger.error(f"Error fetching from {source.name}: {e}")
            source_stats[source.name] = 0
            error_count += 1
            continue
    
    # Final deduplication across all sources
    logger.info(f"Total articles fetched: {len(all_articles)}")
    unique_articles = fetcher.deduplicate_articles(all_articles)
    logger.info(f"Unique articles after deduplication: {len(unique_articles)}")
    
    # Prepare articles for storage
    # Note: We don't filter here - bulk_store_articles will handle it efficiently
    new_articles = unique_articles
    if not force_refresh and existing_urls:
        # Log how many will be skipped
        existing_count = len([a for a in unique_articles if a.get('url') in existing_urls])
        logger.info(f"Found {existing_count} existing articles (will be skipped)")
        logger.info(f"Will store {len(unique_articles) - existing_count} new articles")
    
    if not new_articles:
        logger.info("No new articles to store")
        return {
            'stored': 0,
            'updated': 0,
            'skipped': len(unique_articles),
            'sources': source_stats,
            'total_fetched': len(all_articles),
            'unique': len(unique_articles)
        }
    
    # Store articles in bulk
    logger.info(f"Storing {len(new_articles)} articles...")
    stored, updated, skipped = store_articles_bulk(
        repo,
        new_articles,
        existing_urls,
        force_refresh
    )
    
    # Note: last_fetched timestamps are updated immediately after each source fetch
    # (see loop above) to track progress even if storage fails
    
    logger.info("=" * 60)
    logger.info("Process Complete!")
    logger.info(f"  Stored: {stored} articles")
    logger.info(f"  Updated: {updated} articles")
    logger.info(f"  Skipped: {skipped} articles (duplicates/existing)")
    logger.info(f"  Total fetched: {len(all_articles)} articles")
    logger.info(f"  Unique: {len(unique_articles)} articles")
    logger.info("=" * 60)
    
    return {
        'stored': stored,
        'updated': updated,
        'skipped': skipped,
        'sources': source_stats,
        'total_fetched': len(all_articles),
        'unique': len(unique_articles)
    }


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch and store news articles with optimized incremental updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Incremental fetch (default: only new articles since last run)
  python scripts/fetch_and_store_news.py
  
  # Update only last 7 days
  python scripts/fetch_and_store_news.py --update-recent 7
  
  # Force refresh all articles from last 30 days
  python scripts/fetch_and_store_news.py --force-refresh
  
  # Custom date range
  python scripts/fetch_and_store_news.py --start-date 2024-01-01 --end-date 2024-01-31
  
  # Fetch from specific sources only
  python scripts/fetch_and_store_news.py --sources economic_times_markets moneycontrol_latest
  
  # Force refresh with custom date range
  python scripts/fetch_and_store_news.py --force-refresh --start-date 2024-01-01 --end-date 2024-01-31
        """
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force re-fetch and update all articles even if they already exist'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for article fetch (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format). Default: latest article date or 30 days ago'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for article fetch (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format). Default: now'
    )
    
    parser.add_argument(
        '--update-recent',
        type=int,
        metavar='N',
        help='Update only the last N days of articles (overrides --start-date)'
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        help='List of source names to fetch (e.g., economic_times_markets moneycontrol_latest). Default: all active sources'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=1.0,
        help='Delay in seconds between sources (default: 1.0)'
    )
    
    return parser.parse_args()


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats.
    
    Returns naive datetime in UTC.
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d-%m-%Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # Return naive datetime (assumed UTC)
            return dt
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format.")


def main():
    """Main function."""
    args = parse_arguments()
    
    setup_logging()
    
    # Parse date arguments
    start_date = None
    end_date = None
    if args.start_date:
        start_date = parse_date(args.start_date)
        logger.info(f"Start date: {start_date}")
    if args.end_date:
        end_date = parse_date(args.end_date)
        logger.info(f"End date: {end_date}")
    if args.update_recent:
        logger.info(f"Update recent days: {args.update_recent}")
    if args.force_refresh:
        logger.info("Force refresh: ENABLED")
    if args.sources:
        logger.info(f"Sources: {', '.join(args.sources)}")
    
    # Get database session
    with get_db() as session:
        try:
            stats = fetch_and_store_news(
                session=session,
                start_date=start_date,
                end_date=end_date,
                force_refresh=args.force_refresh,
                update_recent_days=args.update_recent,
                sources=args.sources
            )
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("Summary")
            logger.info("=" * 60)
            logger.info(f"Articles stored: {stats['stored']}")
            logger.info(f"Articles updated: {stats['updated']}")
            logger.info(f"Articles skipped: {stats['skipped']}")
            logger.info(f"Total fetched: {stats['total_fetched']}")
            logger.info(f"Unique articles: {stats['unique']}")
            logger.info("\nBy source:")
            for source, count in stats['sources'].items():
                logger.info(f"  {source}: {count} articles")
            
            return 0
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return 1


if __name__ == "__main__":
    sys.exit(main())
