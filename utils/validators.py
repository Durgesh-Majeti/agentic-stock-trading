"""Input validation utilities."""
from typing import Optional
from datetime import datetime, date
from loguru import logger


def validate_price(price: float, previous_price: Optional[float] = None, max_deviation: float = 0.05) -> bool:
    """Validate price with sanity check.
    
    Args:
        price: Price to validate
        previous_price: Previous price for comparison
        max_deviation: Maximum allowed deviation (5% default)
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(price, (int, float)):
        logger.warning(f"Invalid price type: {type(price)}")
        return False
    
    if price <= 0:
        logger.warning(f"Invalid price: {price} (must be > 0)")
        return False
    
    if price > 1000000:  # Sanity check for extremely high prices
        logger.warning(f"Price seems too high: {price}")
        return False
    
    if previous_price:
        if previous_price <= 0:
            logger.warning(f"Invalid previous price: {previous_price}")
            return False
        
        deviation = abs(price - previous_price) / previous_price
        if deviation > max_deviation:
            logger.warning(
                f"Price deviation too high: {deviation:.2%} "
                f"(previous: {previous_price}, current: {price})"
            )
            return False
    
    return True


def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation: alphanumeric, 2-20 characters
    if not symbol.replace(".", "").replace("-", "").isalnum():
        return False
    
    if len(symbol) < 2 or len(symbol) > 20:
        return False
    
    return True


def validate_quantity(quantity: int, min_quantity: int = 1) -> bool:
    """Validate order quantity.
    
    Args:
        quantity: Quantity to validate
        min_quantity: Minimum allowed quantity
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(quantity, int) or quantity < min_quantity:
        logger.warning(f"Invalid quantity: {quantity} (must be >= {min_quantity})")
        return False
    
    if quantity > 1000000:  # Sanity check
        logger.warning(f"Quantity seems too high: {quantity}")
        return False
    
    return True


def validate_confidence_score(score: float) -> bool:
    """Validate confidence score (0-100).
    
    Args:
        score: Confidence score to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(score, (int, float)) or score < 0 or score > 100:
        logger.warning(f"Invalid confidence score: {score} (must be 0-100)")
        return False
    return True


def validate_percentage(value: float, min_value: float = 0.0, max_value: float = 100.0) -> bool:
    """Validate percentage value.
    
    Args:
        value: Percentage value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False
    
    if value < min_value or value > max_value:
        logger.warning(f"Invalid percentage: {value} (must be {min_value}-{max_value})")
        return False
    
    return True


def validate_date(date_value: date) -> bool:
    """Validate date object.
    
    Args:
        date_value: Date to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(date_value, date):
        return False
    
    # Check if date is not too far in the future
    if date_value > date.today():
        logger.warning(f"Date is in the future: {date_value}")
        return False
    
    # Check if date is not too far in the past (more than 10 years)
    if date_value < date(date.today().year - 10, 1, 1):
        logger.warning(f"Date is too far in the past: {date_value}")
        return False
    
    return True


def validate_datetime(dt: datetime) -> bool:
    """Validate datetime object.
    
    Args:
        dt: Datetime to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(dt, datetime):
        return False
    
    # Check if datetime is not too far in the future
    if dt > datetime.now():
        logger.warning(f"Datetime is in the future: {dt}")
        return False
    
    return True


def validate_email(email: str) -> bool:
    """Validate email address (basic validation).
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    if "@" not in email or "." not in email:
        return False
    
    # Split into local part and domain part
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local_part, domain_part = parts
    
    # Check that local part exists and is not empty
    if not local_part or len(local_part) == 0:
        return False
    
    # Check that domain part exists and contains a dot
    if not domain_part or "." not in domain_part:
        return False
    
    # Check overall length
    if len(email) < 5 or len(email) > 254:
        return False
    
    return True


def validate_api_key(api_key: str, min_length: int = 10) -> bool:
    """Validate API key format.
    
    Args:
        api_key: API key to validate
        min_length: Minimum length
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(api_key, str):
        return False
    
    if len(api_key) < min_length:
        return False
    
    # Basic check: should contain alphanumeric characters
    if not api_key.replace("-", "").replace("_", "").isalnum():
        return False
    
    return True


def validate_stop_loss_target(entry_price: float, stop_loss: float, target: float) -> bool:
    """Validate stop loss and target prices relative to entry.
    
    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        target: Target price
        
    Returns:
        True if valid, False otherwise
    """
    if not all(isinstance(x, (int, float)) for x in [entry_price, stop_loss, target]):
        return False
    
    if entry_price <= 0:
        return False
    
    # Stop loss should be below entry for BUY
    if stop_loss >= entry_price:
        logger.warning(f"Stop loss {stop_loss} should be below entry {entry_price}")
        return False
    
    # Target should be above entry for BUY
    if target <= entry_price:
        logger.warning(f"Target {target} should be above entry {entry_price}")
        return False
    
    # Risk:Reward ratio should be at least 1:2
    risk = entry_price - stop_loss
    reward = target - entry_price
    
    if risk <= 0 or reward <= 0:
        return False
    
    if reward / risk < 1.5:  # At least 1.5:1 reward:risk
        logger.warning(f"Risk:Reward ratio too low: {reward/risk:.2f}")
        return False
    
    return True
