# Updated .env File Template

**Date**: January 2025  
**Purpose**: Complete .env file template for local Ollama configuration

---

## Complete .env File

Copy this content to your `.env` file:

```env
# ============================================
# OLLAMA LOCAL CONFIGURATION
# ============================================
# Local Ollama server URL (default: http://localhost:11434)
# Make sure Ollama is running: ollama serve
OLLAMA_BASE_URL=http://localhost:11434

# Strategy Specialist Models (must be pulled locally)
# Primary: deepseek-r1:7b (thinking mode, financial modeling)
# Fallback: qwen2.5:7b
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_STRATEGY_FALLBACK=qwen2.5:7b

# Database Librarian Models (must be pulled locally)
# Primary: qwen2.5-coder:7b-instruct (SQL generation, code optimization)
# Fallback: codegemma:7b
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_DATABASE_FALLBACK=codegemma:7b

# Telegram Assistant Models (must be pulled locally)
# Primary: gemma2:2b-instruct-q4_K_M (quantized for speed)
# Fallback: phi3:mini
OLLAMA_CHATBOT_MODEL=gemma2:2b-instruct-q4_K_M
OLLAMA_CHATBOT_FALLBACK=phi3:mini

# Portfolio Guardian Model (must be pulled locally)
# Uses same model as Strategy Specialist
OLLAMA_GUARDIAN_MODEL=deepseek-r1:7b

# ============================================
# TELEGRAM BOT CONFIGURATION
# ============================================
# Get bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Get chat ID by sending a message to your bot and visiting:
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
TELEGRAM_CHAT_ID=your_chat_id_here

# ============================================
# SHOONYA API (PRIMARY BROKER)
# ============================================
# Get from Prism Portal: https://prism.shoonya.com
SHOONYA_USER_ID=your_shoonya_user_id
SHOONYA_PASSWORD=your_shoonya_password
SHOONYA_TWO_FA=your_2fa_key
SHOONYA_VENDOR_CODE=your_vendor_code
SHOONYA_API_SECRET=your_api_secret
SHOONYA_IMEI=your_imei

# ============================================
# UPSTOX API (BACKUP BROKER) - Optional
# ============================================
# Get from Upstox Developer Portal: https://account.upstox.com/developer/apps
UPSTOX_API_KEY=your_upstox_api_key
UPSTOX_API_SECRET=your_upstox_api_secret
UPSTOX_REDIRECT_URI=http://localhost:8080/callback
UPSTOX_ACCESS_TOKEN=your_access_token

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=sqlite:///./data/trading.db

# ============================================
# RISK PARAMETERS
# ============================================
# Maximum position size per trade (in INR)
MAX_POSITION_SIZE=10000.0

# Risk percentage per trade (2% default)
RISK_PERCENTAGE=2.0

# Stop loss percentage (2% default)
STOP_LOSS_PERCENTAGE=2.0

# Target profit percentage (4% default)
TARGET_PERCENTAGE=4.0

# Maximum daily loss limit (in INR)
MAX_DAILY_LOSS=10000.0

# Maximum sector exposure (20% = 0.20)
MAX_SECTOR_EXPOSURE=0.20

# Maximum concurrent positions
MAX_CONCURRENT_POSITIONS=5

# Portfolio heat threshold (80% = block new trades)
PORTFOLIO_HEAT_THRESHOLD=80.0

# ============================================
# TRADING SETTINGS
# ============================================
# Enable live trading (false = paper trading)
ENABLE_LIVE_TRADING=false

# Trading mode: paper or live
TRADING_MODE=paper

# Market hours (IST)
MARKET_HOURS_START=09:15
MARKET_HOURS_END=15:30
TIMEZONE=Asia/Kolkata

# ============================================
# WATCHLIST
# ============================================
# Comma-separated list of stock symbols
WATCHLIST=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK

# ============================================
# DATA COLLECTION INTERVALS (in seconds)
# ============================================
# Market data update interval (5 minutes = 300 seconds)
DATA_UPDATE_INTERVAL=300

# Sentiment analysis update interval (10 minutes = 600 seconds)
# News articles are fetched and analyzed every 10 minutes during market hours
SENTIMENT_UPDATE_INTERVAL=600

# Heartbeat interval (30 minutes = 1800 seconds)
HEARTBEAT_INTERVAL=1800

# Stop loss check interval (5 minutes = 300 seconds)
STOP_LOSS_CHECK_INTERVAL=300

# Portfolio heat check interval (5 minutes = 300 seconds)
PORTFOLIO_HEAT_CHECK_INTERVAL=300

# ============================================
# LOGGING CONFIGURATION
# ============================================
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path
LOG_FILE=./logs/trading_app.log

# Log rotation (daily)
LOG_ROTATION=1 day

# Log retention (30 days)
LOG_RETENTION=30 days
```

---

## Migration from Old .env

### Remove These (Old Ollama Cloud Settings):
```env
OLLAMA_API_KEY=...
OLLAMA_HOST=ollama.com
```

### Replace With (Local Ollama Settings):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_STRATEGY_FALLBACK=qwen2.5:7b
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_DATABASE_FALLBACK=codegemma:7b
OLLAMA_CHATBOT_MODEL=gemma2:2b-instruct-q4_K_M
OLLAMA_CHATBOT_FALLBACK=phi3:mini
OLLAMA_GUARDIAN_MODEL=deepseek-r1:7b
```

### Update Model Names:
- `deepseek-v3.1:671b` → `deepseek-r1:7b`
- `gpt-oss:120b` → `qwen2.5:7b`
- `qwen3-coder:480b` → `qwen2.5-coder:7b-instruct`
- `devstral-2:123b` → `codegemma:7b`
- `gemini-3-flash-preview` → `gemma2:2b-instruct-q4_K_M`
- `nemotron-3-nano:30b` → `phi3:mini`

---

## Quick Setup

1. **Copy the template above** to your `.env` file
2. **Fill in your credentials**:
   - Telegram bot token
   - Shoonya API credentials
   - Upstox API credentials (optional)
3. **Keep existing values** for:
   - Database URL
   - Risk parameters
   - Trading settings
   - Watchlist
   - Intervals

---

**Note**: The Settings class now ignores extra fields, so old cloud settings won't cause errors, but it's recommended to update your `.env` file.
