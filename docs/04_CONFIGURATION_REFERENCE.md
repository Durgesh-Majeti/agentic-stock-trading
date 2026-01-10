# Configuration Reference Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Configuration Files](#configuration-files)
4. [Model Configuration](#model-configuration)
5. [Risk Parameters](#risk-parameters)
6. [API Credentials](#api-credentials)
7. [Database Configuration](#database-configuration)
8. [Logging Configuration](#logging-configuration)
9. [Trading Settings](#trading-settings)
10. [Best Practices](#best-practices)

---

## Overview

### Configuration Sources

Configuration is loaded from:
1. **`.env` file** (primary)
2. **Environment variables** (override)
3. **Default values** (fallback)

### Configuration Management

- **Pydantic Settings**: Type validation
- **Environment-specific**: Dev/Prod configs
- **Secrets Management**: Never commit `.env`

---

## Environment Variables

### Complete `.env` Template

```env
# ============================================
# OLLAMA LOCAL CONFIGURATION
# ============================================
OLLAMA_BASE_URL=http://localhost:11434

# Strategy Specialist Models (must be pulled locally)
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_STRATEGY_FALLBACK=qwen2.5:7b

# Database Librarian Models (must be pulled locally)
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_DATABASE_FALLBACK=codegemma:7b

# Telegram Assistant Models (must be pulled locally)
OLLAMA_CHATBOT_MODEL=gemma2:2b-instruct-q4_K_M
OLLAMA_CHATBOT_FALLBACK=phi3:mini

# Portfolio Guardian Model (must be pulled locally)
OLLAMA_GUARDIAN_MODEL=deepseek-r1:7b

# ============================================
# TELEGRAM BOT
# ============================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ============================================
# SHOONYA API (Primary Broker)
# ============================================
SHOONYA_USER_ID=your_user_id
SHOONYA_PASSWORD=your_password
SHOONYA_TWO_FA=your_2fa_key
SHOONYA_VENDOR_CODE=your_vendor_code
SHOONYA_API_SECRET=your_api_secret
SHOONYA_IMEI=your_imei

# ============================================
# UPSTOX API (Backup Broker)
# ============================================
UPSTOX_API_KEY=your_upstox_api_key
UPSTOX_API_SECRET=your_upstox_api_secret
UPSTOX_REDIRECT_URI=http://localhost:8080/callback
UPSTOX_ACCESS_TOKEN=your_access_token

# ============================================
# DATABASE
# ============================================
DATABASE_URL=sqlite:///./data/trading.db

# ============================================
# RISK PARAMETERS
# ============================================
MAX_POSITION_SIZE=50000.0
RISK_PERCENTAGE=2.0
STOP_LOSS_PERCENTAGE=2.0
TARGET_PERCENTAGE=4.0
MAX_DAILY_LOSS=10000.0
MAX_SECTOR_EXPOSURE=0.20
MAX_CONCURRENT_POSITIONS=5
PORTFOLIO_HEAT_THRESHOLD=80.0

# ============================================
# TRADING SETTINGS
# ============================================
ENABLE_LIVE_TRADING=false
TRADING_MODE=paper
MARKET_HOURS_START=09:15
MARKET_HOURS_END=15:30
TIMEZONE=Asia/Kolkata

# ============================================
# WATCHLIST
# ============================================
WATCHLIST=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK

# ============================================
# DATA COLLECTION INTERVALS (in seconds)
# ============================================
DATA_UPDATE_INTERVAL=300          # Market data update (5 minutes)
SENTIMENT_UPDATE_INTERVAL=600     # News sentiment update (10 minutes)
HEARTBEAT_INTERVAL=1800           # System heartbeat (30 minutes)
STOP_LOSS_CHECK_INTERVAL=300     # Stop loss monitoring (5 minutes)
PORTFOLIO_HEAT_CHECK_INTERVAL=300 # Portfolio heat check (5 minutes)

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
LOG_FILE=./logs/trading_app.log
LOG_ROTATION=1 day
LOG_RETENTION=30 days
```

---

## Configuration Files

### `config/settings.py`

```python
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    # Ollama Local Configuration
    ollama_base_url: str = "http://localhost:11434"
    
    # Model Configuration (must be pulled locally)
    ollama_strategy_model: str = "deepseek-r1:7b"
    ollama_strategy_fallback: str = "qwen2.5:7b"
    ollama_database_model: str = "qwen2.5-coder:7b-instruct"
    ollama_database_fallback: str = "codegemma:7b"
    ollama_chatbot_model: str = "gemma2:2b-instruct-q4_K_M"
    ollama_chatbot_fallback: str = "phi3:mini"
    ollama_guardian_model: str = "deepseek-r1:7b"
    
    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Shoonya
    shoonya_user_id: str = ""
    shoonya_password: str = ""
    shoonya_two_fa: str = ""
    shoonya_vendor_code: str = ""
    shoonya_api_secret: str = ""
    shoonya_imei: str = ""
    
    # Upstox
    upstox_api_key: str = ""
    upstox_api_secret: str = ""
    upstox_redirect_uri: str = "http://localhost:8080/callback"
    upstox_access_token: str = ""
    
    # Database
    database_url: str = "sqlite:///./data/trading.db"
    
    # Risk Parameters
    max_position_size: float = 50000.0
    risk_percentage: float = 2.0
    stop_loss_percentage: float = 2.0
    target_percentage: float = 4.0
    max_daily_loss: float = 10000.0
    max_sector_exposure: float = 0.20
    max_concurrent_positions: int = 5
    portfolio_heat_threshold: float = 80.0
    
    # Trading Settings
    enable_live_trading: bool = False
    trading_mode: str = "paper"
    market_hours_start: str = "09:15"
    market_hours_end: str = "15:30"
    timezone: str = "Asia/Kolkata"
    
    # Watchlist
    watchlist: str = "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK"
    
    # Data Collection
    data_update_interval: int = 300
    sentiment_update_interval: int = 600
    heartbeat_interval: int = 1800
    stop_loss_check_interval: int = 300
    portfolio_heat_check_interval: int = 300
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/trading_app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    
    @property
    def watchlist_symbols(self) -> List[str]:
        """Get watchlist as list."""
        return [s.strip().upper() for s in self.watchlist.split(",") if s.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
```

---

## Model Configuration

### Strategy Specialist

**Primary Model**: `deepseek-r1:7b`
- **Temperature**: 0.3
- **Use Case**: Trade signal generation
- **Features**: Thinking mode, financial modeling
- **Size**: ~4.1GB (must be pulled locally)

**Fallback Model**: `qwen2.5:7b`
- **Temperature**: 0.3
- **Use Case**: Backup when primary fails
- **Size**: ~4.4GB

### News Sentiment Analyst

**Primary Model**: `deepseek-r1:7b`
- **Temperature**: 0.3 (consistent sentiment analysis)
- **Use Case**: News sentiment analysis and macro categorization
- **Features**: Complex reasoning, structured JSON output
- **Size**: ~4.1GB (shared with Strategy Specialist)

**Fallback Model**: `qwen2.5:7b`
- **Temperature**: 0.3
- **Use Case**: Backup when primary fails
- **Size**: ~4.4GB

**Note**: FinBERT and VADER are optional optimizations for simple articles. DeepSeek R1 7B is the primary analyzer.

### Database Librarian

**Primary Model**: `qwen2.5-coder:7b-instruct`
- **Temperature**: 0.1 (precision critical)
- **Use Case**: SQL generation
- **Features**: Code optimization, query translation
- **Size**: ~4.4GB

**Fallback Model**: `codegemma:7b`
- **Temperature**: 0.1
- **Use Case**: Backup SQL generation
- **Size**: ~4.8GB

### Telegram Assistant

**Primary Model**: `gemma2:2b-instruct-q4_K_M`
- **Temperature**: 0.7 (natural conversation)
- **Use Case**: User interaction
- **Features**: Fast, lightweight, quantized (Q4_K_M) for speed
- **Size**: ~1.4GB (quantized)

**Fallback Model**: `phi3:mini`
- **Temperature**: 0.7
- **Use Case**: Backup chatbot
- **Size**: ~2.3GB

### News Sentiment Analyst

**Primary Model**: `deepseek-r1:7b`
- **Temperature**: 0.3 (consistent sentiment analysis)
- **Use Case**: News sentiment analysis and macro categorization
- **Features**: Complex reasoning, structured JSON output, macro propagation
- **Size**: ~4.1GB (shared with Strategy Specialist)

**Fallback Model**: `qwen2.5:7b`
- **Temperature**: 0.3
- **Use Case**: Backup when primary fails
- **Size**: ~4.4GB

**Optional Tools**:
- **FinBERT**: Fast sentiment for simple articles (requires transformers + torch)
- **VADER**: Rule-based sentiment (requires nltk)

### Portfolio Guardian

**Primary Model**: `deepseek-r1:7b`
- **Temperature**: 0.2
- **Use Case**: Portfolio monitoring and risk analysis
- **Size**: ~4.1GB

---

## Risk Parameters

### Position Sizing

- **MAX_POSITION_SIZE**: ₹50,000 (max per trade)
- **RISK_PERCENTAGE**: 2% (max portfolio risk per trade)
- **MAX_CONCURRENT_POSITIONS**: 5 (max open positions)

### Stop Loss & Targets

- **STOP_LOSS_PERCENTAGE**: 2% (max loss from entry)
- **TARGET_PERCENTAGE**: 4% (target profit)
- **Risk:Reward Ratio**: Minimum 2:1

### Portfolio Limits

- **MAX_SECTOR_EXPOSURE**: 20% (max sector concentration)
- **PORTFOLIO_HEAT_THRESHOLD**: 80% (max total exposure)
- **MAX_DAILY_LOSS**: ₹10,000 (daily loss limit)

---

## API Credentials

### Ollama Local

1. **Install Ollama**: Download from [ollama.com](https://ollama.com/download)
   - Windows: `winget install Ollama.Ollama`
   - Or download installer from website
2. **Start Ollama Server**: Run `ollama serve` in terminal
3. **Set OLLAMA_BASE_URL**: Default is `http://localhost:11434`
4. **Pull Models**: Run `ollama pull <model_name>` for each required model

### Telegram Bot

1. **Create Bot**: Message @BotFather on Telegram
2. **Get Token**: Copy bot token
3. **Get Chat ID**: Use @userinfobot
4. **Set TELEGRAM_BOT_TOKEN**: Bot token
5. **Set TELEGRAM_CHAT_ID**: Your chat ID

### Shoonya API

1. **Register**: [Shoonya](https://shoonya.com)
2. **Get API Key**: [Prism Portal](https://prism.shoonya.com)
3. **Set Credentials**: All Shoonya variables

### Upstox API

1. **Register**: [Upstox Developer Portal](https://developer.upstox.com)
2. **Create App**: Get API key and secret
3. **Set Credentials**: All Upstox variables

---

## Database Configuration

### SQLite Settings

- **Location**: `data/trading.db`
- **Backup**: Daily automated
- **Size**: ~2GB expected
- **Connection**: Single writer (SQLite limitation)

### Connection String

```
DATABASE_URL=sqlite:///./data/trading.db
```

### Backup Configuration

- **Frequency**: Daily at 4:00 AM
- **Retention**: 7 days daily, 4 weeks weekly
- **Location**: `backups/` directory

---

## Logging Configuration

### Log Levels

- **DEBUG**: Detailed debugging info
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Rotation

- **Rotation**: Daily
- **Retention**: 30 days
- **Format**: Structured JSON
- **Location**: `logs/` directory

### Example Configuration

```python
from loguru import logger

logger.add(
    "logs/trading_app.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time} | {level} | {message}",
    compression="zip"
)
```

---

## Trading Settings

### Trading Modes

- **paper**: Paper trading (simulation)
- **live**: Live trading (real money)

### Market Hours

- **Start**: 09:15 IST
- **End**: 15:30 IST
- **Timezone**: Asia/Kolkata

### Safety Settings

- **ENABLE_LIVE_TRADING**: `false` (default)
- **Manual Approval**: Always required
- **Kill Switch**: `/kill` command available

---

## Best Practices

### Security

1. **Never commit `.env`**: Add to `.gitignore`
2. **Rotate credentials**: Regularly update API keys
3. **Use secrets manager**: For production
4. **Limit access**: Only necessary permissions

### Configuration Management

1. **Version control**: Track config changes
2. **Environment-specific**: Separate dev/prod configs
3. **Documentation**: Document all settings
4. **Validation**: Use Pydantic for type checking

### Performance

1. **Optimize intervals**: Balance freshness vs API limits
2. **Cache data**: Reduce redundant API calls
3. **Batch operations**: Group similar operations
4. **News fetching**: Use rate limiting (15-30 min intervals)
5. **Sentiment analysis**: Batch process articles (10-20 at a time)

### Sentiment Analysis

1. **Primary tool**: Use DeepSeek R1 7B (already in system)
2. **Optional optimization**: Add FinBERT/VADER only if needed for speed
3. **News sources**: Start with 3-4 sources, add more gradually
4. **Data retention**: Clean up old articles (30 days) regularly
5. **Macro propagation**: Review sector impact matrix periodically
4. **Monitor usage**: Track API rate limits

---

**Next Documents**:
- `05_DEPLOYMENT_AND_OPERATIONS.md` - Deployment guide
- `06_TROUBLESHOOTING_AND_DEBUGGING.md` - Troubleshooting guide
