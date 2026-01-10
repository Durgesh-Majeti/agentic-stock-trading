"""Helper utility functions."""
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from pathlib import Path
import json


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    return f"{currency}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage.
    
    Args:
        value: Value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string or "N/A"
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def format_date(d: Optional[date], format_str: str = "%Y-%m-%d") -> str:
    """Format date.
    
    Args:
        d: Date object
        format_str: Format string
        
    Returns:
        Formatted date string or "N/A"
    """
    if d is None:
        return "N/A"
    return d.strftime(format_str)


def is_market_hours(dt: Optional[datetime] = None) -> bool:
    """Check if current time is within market hours (9:15 AM - 3:30 PM IST).
    
    Args:
        dt: Datetime to check (default: current time)
        
    Returns:
        True if market is open, False otherwise
    """
    from config.constants import MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE
    
    if dt is None:
        dt = datetime.now()
    
    current_hour = dt.hour
    current_minute = dt.minute
    
    # Market opens at 9:15 AM
    if current_hour < MARKET_OPEN_HOUR or (current_hour == MARKET_OPEN_HOUR and current_minute < MARKET_OPEN_MINUTE):
        return False
    
    # Market closes at 3:30 PM
    if current_hour > MARKET_CLOSE_HOUR or (current_hour == MARKET_CLOSE_HOUR and current_minute > MARKET_CLOSE_MINUTE):
        return False
    
    # Check if weekend (Saturday=5, Sunday=6)
    if dt.weekday() >= 5:
        return False
    
    return True


def calculate_pnl(entry_price: float, exit_price: float, quantity: int) -> float:
    """Calculate profit/loss.
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        quantity: Quantity
        
    Returns:
        P&L amount
    """
    return (exit_price - entry_price) * quantity


def calculate_pnl_percentage(entry_price: float, exit_price: float) -> float:
    """Calculate profit/loss percentage.
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        
    Returns:
        P&L percentage
    """
    if entry_price == 0:
        return 0.0
    return ((exit_price - entry_price) / entry_price) * 100


def calculate_stop_loss_price(entry_price: float, stop_loss_percent: float) -> float:
    """Calculate stop loss price.
    
    Args:
        entry_price: Entry price
        stop_loss_percent: Stop loss percentage
        
    Returns:
        Stop loss price
    """
    return entry_price * (1 - stop_loss_percent / 100)


def calculate_target_price(entry_price: float, target_percent: float) -> float:
    """Calculate target price.
    
    Args:
        entry_price: Entry price
        target_percent: Target percentage
        
    Returns:
        Target price
    """
    return entry_price * (1 + target_percent / 100)


def get_nifty_500_symbols() -> List[str]:
    """Get list of Nifty 500 symbols (placeholder - should be loaded from file/API).
    
    Returns:
        List of stock symbols
    """
    # This is a placeholder - in production, load from a file or API
    return [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "HINDUNILVR", "BHARTIARTL", "SBIN", "BAJFINANCE", "KOTAKBANK"
    ]


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if not.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary from JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save dictionary to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save file
    """
    ensure_directory(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def get_date_range(start_date: date, end_date: date) -> List[date]:
    """Get list of dates between start and end (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of dates
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, return default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def round_to_precision(value: float, precision: int = 2) -> float:
    """Round value to specified precision.
    
    Args:
        value: Value to round
        precision: Number of decimal places
        
    Returns:
        Rounded value
    """
    return round(value, precision)
