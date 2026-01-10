"""yfinance data fetcher for historical market data."""
import yfinance as yf
import pandas as pd
import requests
import io
import time
from typing import Optional, Dict, List
from datetime import datetime, date, timedelta
from loguru import logger


class YFinanceFetcher:
    """Fetcher for historical market data using yfinance."""
    
    # Browser-like headers to avoid blocking by servers
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self):
        """Initialize yfinance fetcher."""
        self.base_url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    
    def get_nifty_500_symbols(self) -> List[Dict[str, str]]:
        """Fetch Nifty 500 symbol list from NSE website.
        
        Returns:
            List of dictionaries with symbol, company_name, and sector info
        """
        try:
            logger.info("Fetching Nifty 500 symbol list...")
            # Use browser-like headers to avoid blocking
            response = requests.get(self.base_url, headers=self.BROWSER_HEADERS, timeout=30)
            response.raise_for_status()
            
            # Read CSV - try different encodings
            try:
                df = pd.read_csv(io.StringIO(response.text))
            except UnicodeDecodeError:
                # Try with UTF-8 encoding explicitly
                df = pd.read_csv(io.BytesIO(response.content), encoding='utf-8')
            
            symbols = []
            
            # CSV column order: Company Name, Industry, Symbol, Series, ISIN Code
            # We need: Company Name (col 0), Industry (col 1), Symbol (col 2)
            
            # Try to identify columns by name first (more robust)
            name_col = None
            industry_col = None
            symbol_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'company' in col_lower and 'name' in col_lower:
                    name_col = col
                elif 'industry' in col_lower:
                    industry_col = col
                elif 'symbol' in col_lower and 'isin' not in col_lower:
                    symbol_col = col
            
            # Fallback to positional if column names not found
            # Expected order: Company Name (0), Industry (1), Symbol (2), Series (3), ISIN Code (4)
            if name_col is None and len(df.columns) > 0:
                name_col = df.columns[0]
            if industry_col is None and len(df.columns) > 1:
                industry_col = df.columns[1]
            if symbol_col is None and len(df.columns) > 2:
                symbol_col = df.columns[2]
            
            for _, row in df.iterrows():
                try:
                    # Extract symbol from column 2 (Symbol column)
                    if symbol_col:
                        symbol = str(row[symbol_col]).strip().upper() if pd.notna(row[symbol_col]) else None
                    else:
                        symbol = str(row.iloc[2]).strip().upper() if len(row) > 2 and pd.notna(row.iloc[2]) else None
                    
                    if not symbol or symbol == 'NAN' or len(symbol) < 2:
                        continue
                    
                    # Remove .NS suffix if present
                    if symbol.endswith('.NS'):
                        symbol = symbol[:-3]
                    
                    # Remove Series suffix (like -EQ, -BE, etc.) if present
                    # Keep the base symbol for yfinance
                    if '-' in symbol:
                        symbol = symbol.split('-')[0]
                    
                    # Get company name from column 0
                    if name_col:
                        company_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else symbol
                    else:
                        company_name = str(row.iloc[0]).strip() if len(row) > 0 and pd.notna(row.iloc[0]) else symbol
                    
                    # Get industry/sector from column 1
                    sector = None
                    if industry_col:
                        sector = str(row[industry_col]).strip() if pd.notna(row[industry_col]) else None
                    elif len(row) > 1:
                        sector = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
                    
                    # Skip if symbol is invalid or looks like an ISIN code
                    if not symbol or symbol.startswith('INE') or len(symbol) > 20:
                        continue
                    
                    symbols.append({
                        'symbol': symbol,
                        'name': company_name,
                        'sector': sector
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue
            
            logger.info(f"Fetched {len(symbols)} symbols from Nifty 500 list")
            return symbols
            
        except Exception as e:
            logger.error(f"Error fetching Nifty 500 list: {e}")
            raise
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "2y",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
            period: Period string (e.g., "2y", "1y", "6mo") - used if start/end not provided
            start_date: Start date (optional)
            end_date: End date (optional)
            interval: Data interval ("1d" for daily, "1h" for hourly)
            
        Returns:
            DataFrame with OHLCV data, or None if error
        """
        try:
            # Add .NS suffix for NSE stocks if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol_with_suffix = f"{symbol}.NS"
            else:
                symbol_with_suffix = symbol
            
            ticker = yf.Ticker(symbol_with_suffix)
            
            # Fetch data
            if start_date and end_date:
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    auto_adjust=True,
                    prepost=False
                )
            else:
                df = ticker.history(
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    prepost=False
                )
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # yfinance returns DataFrame with DatetimeIndex
            # Reset index to convert DatetimeIndex to a column (usually named 'Date')
            df.reset_index(inplace=True)
            
            # yfinance typically names the date column 'Date' (capital D)
            # Rename it to lowercase 'date'
            if 'Date' in df.columns:
                df.rename(columns={'Date': 'date'}, inplace=True)
            elif 'Datetime' in df.columns:
                df.rename(columns={'Datetime': 'date'}, inplace=True)
            else:
                # Check if first column is datetime type
                first_col = df.columns[0]
                if pd.api.types.is_datetime64_any_dtype(df[first_col]):
                    df.rename(columns={first_col: 'date'}, inplace=True)
                else:
                    logger.warning(f"Could not find date column for {symbol}. Columns: {df.columns.tolist()}")
                    return None
            
            # Rename all other columns to lowercase
            df.columns = [col.lower().replace(' ', '_') if col != 'date' else 'date' for col in df.columns]
            
            # Ensure we have required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"Missing required columns for {symbol}. Available: {df.columns.tolist()}")
                return None
            
            # Convert date to date object if it's datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Select only required columns
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            # Remove rows with missing data
            df = df.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
            
            # Ensure volume is integer
            df['volume'] = df['volume'].astype(int)
            
            logger.debug(f"Fetched {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """Get company information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company info, or None if error
        """
        try:
            # Add .NS suffix if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol_with_suffix = f"{symbol}.NS"
            else:
                symbol_with_suffix = symbol
            
            ticker = yf.Ticker(symbol_with_suffix)
            info = ticker.info
            
            return {
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'long_name': info.get('longName', info.get('shortName', symbol))
            }
            
        except Exception as e:
            logger.warning(f"Error fetching company info for {symbol}: {e}")
            return None
    
    def batch_fetch_historical_data(
        self,
        symbols: List[str],
        period: str = "2y",
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """Fetch historical data for multiple symbols in batches.
        
        Args:
            symbols: List of stock symbols
            period: Period string (e.g., "2y")
            batch_size: Number of symbols to fetch in each batch
            delay_between_batches: Delay in seconds between batches
            
        Returns:
            Dictionary mapping symbol to DataFrame (or None if error)
        """
        results = {}
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        logger.info(f"Fetching data for {len(symbols)} symbols in {total_batches} batches...")
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} symbols)...")
            
            for symbol in batch:
                df = self.get_historical_data(symbol, period=period)
                results[symbol] = df
                
                # Small delay between individual requests
                time.sleep(0.1)
            
            # Delay between batches
            if i + batch_size < len(symbols):
                logger.debug(f"Waiting {delay_between_batches}s before next batch...")
                time.sleep(delay_between_batches)
        
        successful = sum(1 for df in results.values() if df is not None)
        logger.info(f"Completed: {successful}/{len(symbols)} symbols fetched successfully")
        
        return results
