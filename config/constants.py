"""Application constants and enums."""
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OrderType(str, Enum):
    """Order type enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    """Trade status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STOP_LOSS_HIT = "STOP_LOSS_HIT"
    TARGET_HIT = "TARGET_HIT"


class SignalType(str, Enum):
    """Screening signal type."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class AgentName(str, Enum):
    """Agent names for tracking."""
    STRATEGY_SPECIALIST = "strategy_specialist"
    DATABASE_LIBRARIAN = "database_librarian"
    DATA_SCRAPER = "data_scraper"
    TELEGRAM_ASSISTANT = "telegram_assistant"


class Exchange(str, Enum):
    """Stock exchange enumeration."""
    NSE = "NSE"
    BSE = "BSE"


# Technical Indicators (29 indicators as per Agents.md)
TECHNICAL_INDICATORS = [
    "RSI", "MACD", "MACD_Signal", "MACD_Histogram",
    "Bollinger_Upper", "Bollinger_Lower", "Bollinger_Middle",
    "SMA_20", "SMA_50", "SMA_200",
    "EMA_12", "EMA_26",
    "ADX", "ADX_Positive", "ADX_Negative",
    "Stochastic_K", "Stochastic_D",
    "Williams_R",
    "CCI",
    "ATR",
    "OBV",
    "Volume_SMA",
    "Price_Change", "Price_Change_Percent",
    "High_Low_Range", "High_Low_Range_Percent",
    "Volume_Ratio",
    "Momentum",
    "ROC",  # Rate of Change
]

# Risk Management Constants
DEFAULT_STOP_LOSS_PERCENT = 2.0  # 2% stop loss
DEFAULT_TARGET_PERCENT = 4.0     # 4% target
MAX_PORTFOLIO_RISK_PER_TRADE = 5.0  # 5% max risk per trade

# Data Retention (as per Agents.md)
DAILY_DATA_RETENTION_DAYS = 730  # 2 years
INTRADAY_DATA_RETENTION_DAYS = 60  # 60 days

# Market Hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30
