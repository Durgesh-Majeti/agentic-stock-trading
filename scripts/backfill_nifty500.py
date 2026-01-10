"""Backfill Nifty 500 historical data with technical indicators."""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta
from typing import List, Dict, Optional
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.yfinance_fetcher import YFinanceFetcher
from database.session import get_db
from database.repositories.market_data_repo import MarketDataRepository
from utils.technical_indicators import TechnicalIndicators
from loguru import logger
from config.logging_config import setup_logging


def calculate_indicators_for_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators for a DataFrame.
    
    Note: Technical indicators are calculated on the entire DataFrame,
    then we extract values for each row. This is more efficient than
    calculating row-by-row.
    
    Args:
        df: DataFrame with OHLCV data (must have columns: open, high, low, close, volume)
        
    Returns:
        DataFrame with added indicator columns
    """
    if df.empty or len(df) < 20:
        # Initialize empty indicator columns
        indicator_cols = [
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'adx', 'adx_positive', 'adx_negative',
            'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv',
            'volume_sma', 'price_change', 'price_change_percent',
            'high_low_range', 'high_low_range_percent', 'volume_ratio',
            'momentum', 'roc'
        ]
        for col in indicator_cols:
            if col not in df.columns:
                df[col] = None
        return df
    
    # Ensure required columns exist
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        logger.warning(f"Missing required columns. Available: {df.columns.tolist()}")
        return df
    
    # Calculate indicators for the entire DataFrame
    # We'll calculate them progressively for each row
    indicator_cols = [
        'rsi', 'macd', 'macd_signal', 'macd_histogram',
        'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
        'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
        'adx', 'adx_positive', 'adx_negative',
        'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv',
        'volume_sma', 'price_change', 'price_change_percent',
        'high_low_range', 'high_low_range_percent', 'volume_ratio',
        'momentum', 'roc'
    ]
    
    # Initialize indicator columns
    for col in indicator_cols:
        if col not in df.columns:
            df[col] = None
    
    # Calculate indicators progressively
    # Start from row 20 (need at least 20 rows for some indicators)
    for i in range(20, len(df)):
        # Get window up to current row
        window_df = df.iloc[:i+1].copy()
        
        # Calculate indicators for this window
        indicators = TechnicalIndicators.calculate_all_indicators(window_df)
        
        # Update current row with indicator values
        for key, value in indicators.items():
            if key in df.columns:
                df.at[i, key] = value
    
    return df


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
        
        # Calculate technical indicators
        logger.debug(f"Calculating indicators for {symbol} ({len(df)} rows)...")
        df = calculate_indicators_for_dataframe(df)
        
        # Store data in database
        logger.debug(f"Storing {len(df)} rows for {symbol}...")
        stored_count = 0
        
        for _, row in df.iterrows():
            try:
                # Prepare indicator dictionary
                indicators = {}
                indicator_cols = [
                    'rsi', 'macd', 'macd_signal', 'macd_histogram',
                    'bollinger_upper', 'bollinger_lower', 'bollinger_middle',
                    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
                    'adx', 'adx_positive', 'adx_negative',
                    'stochastic_k', 'stochastic_d', 'williams_r', 'cci', 'atr', 'obv',
                    'volume_sma', 'price_change', 'price_change_percent',
                    'high_low_range', 'high_low_range_percent', 'volume_ratio',
                    'momentum', 'roc'
                ]
                
                for col in indicator_cols:
                    if col in row and pd.notna(row[col]):
                        indicators[col] = float(row[col])
                
                # Add daily data
                repo.add_daily_data(
                    stock_id=stock.id,
                    date=row['date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    **indicators
                )
                stored_count += 1
                
            except Exception as e:
                logger.error(f"Error storing row for {symbol} on {row.get('date')}: {e}")
                continue
        
        logger.info(f"✅ {symbol}: Stored {stored_count}/{len(df)} rows")
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
        default=2.0,
        help='Delay in seconds between batches (default: 2.0)'
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
        
        # Process symbols in batches
        batch_size = args.batch_size
        delay_between_batches = args.batch_delay
        total_symbols = len(symbols_data)
        successful = 0
        failed = 0
        
        logger.info(f"Processing {total_symbols} symbols in batches of {batch_size}...")
        
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
                    successful += 1
                else:
                    failed += 1
                
                # Small delay between symbols
                import time
                time.sleep(0.5)
            
            # Delay between batches
            if i + batch_size < total_symbols:
                logger.info(f"Waiting {delay_between_batches}s before next batch...")
                import time
                time.sleep(delay_between_batches)
        
        logger.info(f"\n{'='*60}")
        logger.info("Backfill Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {successful}/{total_symbols}")
        logger.info(f"❌ Failed: {failed}/{total_symbols}")
        logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
