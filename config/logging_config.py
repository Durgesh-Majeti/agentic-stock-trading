"""Logging configuration with rotation."""
from pathlib import Path
from loguru import logger
from config.settings import settings
import sys


def setup_logging():
    """Setup logging with rotation and formatting."""
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler with rotation
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="1 day",  # Rotate daily
        retention="30 days",  # Keep 30 days of logs
        compression="zip",  # Compress old logs
        backtrace=True,  # Show full stack trace
        diagnose=True,  # Show variable values
    )
    
    # Error file handler (only errors and above)
    error_log_file = log_file.parent / "trading_app_errors.log"
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",  # Keep errors longer
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    logger.info("Logging configured successfully")


def get_logger(name: str = None):
    """Get logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
