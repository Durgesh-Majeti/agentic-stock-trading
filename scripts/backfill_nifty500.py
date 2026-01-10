"""Backfill Nifty 500 historical data with technical indicators (OPTIMIZED)."""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta
from typing import List, Dict, Optional
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.yfinance_fetcher import YFinanceFetcher
from database.session import get_db
from database.repositories.market_data_repo import MarketDataRepository
from utils.technical_indicators import TechnicalIndicators
from loguru import logger
from config.logging_config import setup_logging

# Thread-safe counter for progress tracking
progress_lock = threading.Lock()
successful_count = 0
failed_count = 0


def backfill_symbol(
    symbol: str,
    company_name: str,
    sector: Optional[str],
    fetcher: YFinanceFetcher,
    repo: MarketDataRepository,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    force_refresh: bool = False,
    update_recent_days: Optional[int] = None
) -> bool:
    """Backfill historical data for a single symbol.
    
    Args:
        symbol: Stock symbol
        company_name: Company name
        sector: Sector name (optional)
        fetcher: YFinanceFetcher instance
        repo: MarketDataRepository instance
        start_date: Start date (default: 2 years ago)
        end_date: End date (default: today)
        force_refresh: If True, re-fetch even if data exists
        update_recent_days: If specified, only update last N days (overrides start_date)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set default dates
        if end_date is None:
            end_date = date.today()
        
        # Handle update_recent_days option (overrides start_date)
        if update_recent_days is not None:
            start_date = end_date - timedelta(days=update_recent_days)
            logger.info(f"{symbol}: Updating only last {update_recent_days} days")
        elif start_date is None:
            start_date = end_date - timedelta(days=730)  # 2 years
        
        # Save original start_date before any modifications (for force refresh filtering)
        original_start_date = start_date
        
        # Check if stock exists, create if not
        stock = repo.get_stock_by_symbol(symbol)
        if not stock:
            # Try to get company info
            company_info = fetcher.get_company_info(symbol)
            market_cap = company_info.get('market_cap') if company_info else None
            sector = sector or (company_info.get('sector') if company_info else None)
            
            stock = repo.create_stock(
                symbol=symbol,
                name=company_name,
                exchange="NSE",
                sector=sector,
                market_cap=market_cap
            )
            logger.info(f"Created stock record: {symbol} - {company_name}")
        else:
            # Update sector if provided and different
            if sector and stock.sector != sector:
                repo.update_stock_info(stock.id, sector=sector)
        
        # Check what data we already have (unless force_refresh is True)
        if not force_refresh:
            latest_data = repo.get_latest_daily_data(stock.id)
            if latest_data:
                # If update_recent_days is specified, always fetch that range
                if update_recent_days is not None:
                    # Use the calculated start_date from update_recent_days
                    logger.info(f"{symbol}: Updating last {update_recent_days} days (force update)")
                # If we have recent data, only fetch missing dates
                elif latest_data.date >= start_date:
                    # Check if we need to update
                    if latest_data.date >= end_date - timedelta(days=7):
                        logger.info(f"{symbol}: Data is up to date (latest: {latest_data.date})")
                        return True
                    else:
                        # Fetch only missing dates
                        start_date = latest_data.date + timedelta(days=1)
                        logger.info(f"{symbol}: Fetching data from {start_date} onwards")
        else:
            logger.info(f"{symbol}: Force refresh enabled - re-fetching all data")
            # For force refresh, extend start_date backwards to ensure accurate indicator calculation
            # We need at least 200 days of history for SMA_200 and other long-term indicators
            # This ensures indicators are calculated correctly even for the earliest dates
            indicator_lookback_days = 250  # Extra buffer beyond SMA_200 (200 days)
            extended_start = start_date - timedelta(days=indicator_lookback_days)
            logger.debug(f"{symbol}: Extended start date from {original_start_date} to {extended_start} for accurate indicator calculation")
            start_date = extended_start
        
        # Fetch historical data
        logger.info(f"Fetching data for {symbol} ({start_date} to {end_date})...")
        df = fetcher.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1d"
        )
        
        if df is None or df.empty:
            logger.warning(f"No data returned for {symbol}")
            return False
        
        # Get existing dates for bulk check (optimization)
        existing_dates = repo.get_existing_dates_for_stock(stock.id)
        
        # Filter out existing dates (unless force_refresh)
        if not force_refresh and existing_dates:
            df = df[~df['date'].isin(existing_dates)]
            if df.empty:
                logger.info(f"{symbol}: All data already exists, skipping")
                return True
        
        if df.empty:
            logger.info(f"{symbol}: No new data to store")
            return True
        
        # Calculate technical indicators (VECTORIZED - much faster)
        logger.debug(f"Calculating indicators for {symbol} ({len(df)} rows)...")
        df = TechnicalIndicators.calculate_all_indicators_vectorized(df)
        
        # Prepare data for bulk insert/update
        rows_to_insert = []
        rows_to_update = []
        
        for _, row in df.iterrows():
            try:
                # Validate date
                row_date = row['date']
                if pd.isna(row_date) or row_date == '':
                    logger.warning(f"{symbol}: Skipping row with invalid date")
                    continue
                
                # Ensure date is a date object (not string or datetime)
                if isinstance(row_date, str):
                    try:
                        row_date = date.fromisoformat(row_date)
                    except (ValueError, AttributeError):
                        logger.warning(f"{symbol}: Skipping row with invalid date format: {row_date}")
                        continue
                elif hasattr(row_date, 'date'):
                    row_date = row_date.date()
                elif not isinstance(row_date, date):
                    logger.warning(f"{symbol}: Skipping row with invalid date type: {type(row_date)}")
                    continue
                
                # Prepare data dictionary
                data_dict = {
                    'date': row_date,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'rsi': float(row['rsi']) if pd.notna(row.get('rsi')) else None,
                    'macd': float(row['macd']) if pd.notna(row.get('macd')) else None,
                    'macd_signal': float(row['macd_signal']) if pd.notna(row.get('macd_signal')) else None,
                    'macd_histogram': float(row['macd_histogram']) if pd.notna(row.get('macd_histogram')) else None,
                    'bollinger_upper': float(row['bollinger_upper']) if pd.notna(row.get('bollinger_upper')) else None,
                    'bollinger_lower': float(row['bollinger_lower']) if pd.notna(row.get('bollinger_lower')) else None,
                    'bollinger_middle': float(row['bollinger_middle']) if pd.notna(row.get('bollinger_middle')) else None,
                    'sma_20': float(row['sma_20']) if pd.notna(row.get('sma_20')) else None,
                    'sma_50': float(row['sma_50']) if pd.notna(row.get('sma_50')) else None,
                    'sma_200': float(row['sma_200']) if pd.notna(row.get('sma_200')) else None,
                    'ema_12': float(row['ema_12']) if pd.notna(row.get('ema_12')) else None,
                    'ema_26': float(row['ema_26']) if pd.notna(row.get('ema_26')) else None,
                    'ema_20': float(row['ema_20']) if pd.notna(row.get('ema_20')) else None,
                    'ema_50': float(row['ema_50']) if pd.notna(row.get('ema_50')) else None,
                    'adx': float(row['adx']) if pd.notna(row.get('adx')) else None,
                    'adx_positive': float(row['adx_positive']) if pd.notna(row.get('adx_positive')) else None,
                    'adx_negative': float(row['adx_negative']) if pd.notna(row.get('adx_negative')) else None,
                    'stochastic_k': float(row['stochastic_k']) if pd.notna(row.get('stochastic_k')) else None,
                    'stochastic_d': float(row['stochastic_d']) if pd.notna(row.get('stochastic_d')) else None,
                    'williams_r': float(row['williams_r']) if pd.notna(row.get('williams_r')) else None,
                    'cci': float(row['cci']) if pd.notna(row.get('cci')) else None,
                    'atr': float(row['atr']) if pd.notna(row.get('atr')) else None,
                    'obv': float(row['obv']) if pd.notna(row.get('obv')) else None,
                    'mfi': float(row['mfi']) if pd.notna(row.get('mfi')) else None,
                    'volume_sma': float(row['volume_sma']) if pd.notna(row.get('volume_sma')) else None,
                    'price_change': float(row['price_change']) if pd.notna(row.get('price_change')) else None,
                    'price_change_percent': float(row['price_change_percent']) if pd.notna(row.get('price_change_percent')) else None,
                    'high_low_range': float(row['high_low_range']) if pd.notna(row.get('high_low_range')) else None,
                    'high_low_range_percent': float(row['high_low_range_percent']) if pd.notna(row.get('high_low_range_percent')) else None,
                    'volume_ratio': float(row['volume_ratio']) if pd.notna(row.get('volume_ratio')) else None,
                    'momentum': float(row['momentum']) if pd.notna(row.get('momentum')) else None,
                    'roc': float(row['roc']) if pd.notna(row.get('roc')) else None,
                }
                
                # Check if exists (for update vs insert)
                # For force refresh, we update all dates in the requested range
                # (but only store dates within the original requested range, not the extended lookback)
                if force_refresh:
                    # During force refresh, only update dates within the original requested range
                    # The extended lookback is only for accurate indicator calculation
                    if row_date >= original_start_date:
                        if row_date in existing_dates:
                            rows_to_update.append(data_dict)
                        else:
                            rows_to_insert.append(data_dict)
                    # Skip dates before original_start_date (they're only for indicator calculation context)
                else:
                    # Normal mode: update existing, insert new
                    if row_date in existing_dates:
                        rows_to_update.append(data_dict)
                    else:
                        rows_to_insert.append(data_dict)
                    
            except Exception as e:
                logger.error(f"Error preparing row for {symbol} on {row.get('date')}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                continue
        
        # Bulk insert new rows
        inserted_count = 0
        if rows_to_insert:
            inserted_count = repo.bulk_insert_daily_data(stock.id, rows_to_insert)
            logger.debug(f"{symbol}: Bulk inserted {inserted_count} rows")
        
        # Bulk update existing rows
        updated_count = 0
        if rows_to_update:
            updated_count = repo.bulk_update_daily_data(stock.id, rows_to_update)
            logger.debug(f"{symbol}: Bulk updated {updated_count} rows")
        
        total_stored = inserted_count + updated_count
        logger.info(f"✅ {symbol}: Stored {total_stored} rows ({inserted_count} new, {updated_count} updated)")
        return True
        
    except Exception as e:
        logger.error(f"Error backfilling {symbol}: {e}")
        return False


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Backfill Nifty 500 historical data with technical indicators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard backfill (incremental, 2 years)
  python scripts/backfill_nifty500.py
  
  # Force refresh all data
  python scripts/backfill_nifty500.py --force-refresh
  
  # Update only last 30 days
  python scripts/backfill_nifty500.py --update-recent 30
  
  # Custom date range
  python scripts/backfill_nifty500.py --start-date 2024-01-01 --end-date 2024-12-31
  
  # Force refresh with custom date range
  python scripts/backfill_nifty500.py --force-refresh --start-date 2023-01-01 --end-date 2023-12-31
        """
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force re-fetch all data even if it already exists in database'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for data fetch (YYYY-MM-DD format). Default: 2 years ago'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for data fetch (YYYY-MM-DD format). Default: today'
    )
    
    parser.add_argument(
        '--update-recent',
        type=int,
        metavar='N',
        help='Update only the last N days of data (overrides --start-date)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of symbols to process per batch (default: 10)'
    )
    
    parser.add_argument(
        '--batch-delay',
        type=float,
        default=0.5,
        help='Delay in seconds between batches (default: 0.5)'
    )
    
    parser.add_argument(
        '--symbol-delay',
        type=float,
        default=0.1,
        help='Delay in seconds between symbols (default: 0.1)'
    )
    
    parser.add_argument(
        '--parallel-workers',
        type=int,
        default=3,
        help='Number of parallel workers for processing symbols (default: 3, max: 5)'
    )
    
    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel processing (use sequential processing)'
    )
    
    return parser.parse_args()


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def main():
    """Main backfill function."""
    # Parse command-line arguments
    args = parse_arguments()
    
    setup_logging()
    logger.info("=" * 60)
    logger.info("Nifty 500 Historical Data Backfill")
    logger.info("=" * 60)
    
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
    
    # Initialize components
    fetcher = YFinanceFetcher()
    
    # Get Nifty 500 symbols
    logger.info("Fetching Nifty 500 symbol list...")
    try:
        symbols_data = fetcher.get_nifty_500_symbols()
        logger.info(f"Found {len(symbols_data)} symbols")
    except Exception as e:
        logger.error(f"Failed to fetch symbol list: {e}")
        return
    
    # Get database session
    with get_db() as session:
        repo = MarketDataRepository(session)
        
        # Process symbols
        total_symbols = len(symbols_data)
        global successful_count, failed_count
        successful_count = 0
        failed_count = 0
        
        # Determine processing mode
        use_parallel = not args.no_parallel and args.parallel_workers > 1
        max_workers = min(args.parallel_workers, 5) if use_parallel else 1
        
        if use_parallel:
            logger.info(f"Processing {total_symbols} symbols with {max_workers} parallel workers...")
            logger.info("Using optimized vectorized indicators and bulk database operations")
            
            # Process in parallel
            def process_symbol_wrapper(symbol_data):
                """Wrapper for parallel processing."""
                global successful_count, failed_count
                try:
                    with get_db() as local_session:
                        local_repo = MarketDataRepository(local_session)
                        success = backfill_symbol(
                            symbol=symbol_data['symbol'],
                            company_name=symbol_data['name'],
                            sector=symbol_data.get('sector'),
                            fetcher=fetcher,
                            repo=local_repo,
                            start_date=start_date,
                            end_date=end_date,
                            force_refresh=args.force_refresh,
                            update_recent_days=args.update_recent
                        )
                        
                        with progress_lock:
                            if success:
                                successful_count += 1
                            else:
                                failed_count += 1
                        
                        return success
                except Exception as e:
                    logger.error(f"Error processing {symbol_data['symbol']}: {e}")
                    with progress_lock:
                        failed_count += 1
                    return False
            
            # Process with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for symbol_data in symbols_data:
                    future = executor.submit(process_symbol_wrapper, symbol_data)
                    futures.append(future)
                    # Small delay to avoid rate limiting
                    time.sleep(args.symbol_delay)
                
                # Wait for completion and log progress
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 10 == 0:
                        logger.info(f"Progress: {completed}/{total_symbols} symbols processed")
        else:
            # Sequential processing (original method, but optimized)
            logger.info(f"Processing {total_symbols} symbols sequentially (optimized)...")
            batch_size = args.batch_size
            delay_between_batches = args.batch_delay
            
            for i in range(0, total_symbols, batch_size):
                batch = symbols_data[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_symbols + batch_size - 1) // batch_size
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Batch {batch_num}/{total_batches} ({len(batch)} symbols)")
                logger.info(f"{'='*60}")
                
                for symbol_data in batch:
                    symbol = symbol_data['symbol']
                    name = symbol_data['name']
                    sector = symbol_data.get('sector')
                    
                    success = backfill_symbol(
                        symbol=symbol,
                        company_name=name,
                        sector=sector,
                        fetcher=fetcher,
                        repo=repo,
                        start_date=start_date,
                        end_date=end_date,
                        force_refresh=args.force_refresh,
                        update_recent_days=args.update_recent
                    )
                    
                    if success:
                        successful_count += 1
                    else:
                        failed_count += 1
                    
                    # Small delay between symbols
                    time.sleep(args.symbol_delay)
                
                # Delay between batches
                if i + batch_size < total_symbols:
                    logger.info(f"Waiting {delay_between_batches}s before next batch...")
                    time.sleep(delay_between_batches)
    
    logger.info(f"\n{'='*60}")
    logger.info("Backfill Complete!")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {successful_count}/{total_symbols}")
    logger.info(f"❌ Failed: {failed_count}/{total_symbols}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
