# API Integration Summary

**Version**: 1.0  
**Last Updated**: January 2025

---

## Overview

This document provides a quick reference for all API integrations used in the Agentic Stock Trading System.

---

## API Integrations

### 1. Shoonya API (Primary Broker)

**Purpose**: Primary trading platform and real-time data source

**Type**: REST API + WebSocket

**Authentication**: Session-based with TOTP 2FA

**Key Features**:
- Real-time market data via WebSocket (500+ instruments)
- Order placement and management
- Portfolio and holdings
- Historical data

**Rate Limits**:
- Quotes: 10 requests/second
- Orders: 20 orders/second
- WebSocket: Unlimited (after connection)

**Documentation**: [SHOONYA_API_GUIDE.md](SHOONYA_API_GUIDE.md)

**Status**: ✅ Primary data source

---

### 2. Upstox API (Backup Broker)

**Purpose**: Backup data source and trading platform

**Type**: REST API + WebSocket

**Authentication**: OAuth 2.0 (Authorization Code Flow)

**Key Features**:
- Market data (backup)
- Order management
- Portfolio information
- Historical data

**Rate Limits**:
- 50 requests/second
- 500 requests/minute
- 100,000 requests/day

**Documentation**: [UPSTOX_API_GUIDE.md](UPSTOX_API_GUIDE.md)

**Status**: ✅ Backup/fallback data source

---

### 3. Local Ollama (LLM Service)

**Purpose**: Local LLM inference for all agents

**Type**: Local HTTP API

**Authentication**: None (local server)

**Key Features**:
- Multiple models per agent role
- Automatic fallback
- No rate limits
- Offline capable

**Models**:
- Strategy: `deepseek-r1:7b` / `qwen2.5:7b`
- Database: `qwen2.5-coder:7b-instruct` / `codegemma:7b`
- Chatbot: `gemma2:2b-instruct-q4_K_M` / `phi3:mini`
- Guardian: `deepseek-r1:7b`

**Base URL**: `http://localhost:11434`

**Documentation**: [OLLAMA_LOCAL_SETUP.md](OLLAMA_LOCAL_SETUP.md)

**Status**: ✅ Core LLM service

---

### 4. Telegram Bot API

**Purpose**: User interface and trade approvals

**Type**: REST API (via python-telegram-bot)

**Authentication**: Bot token from @BotFather

**Key Features**:
- Text commands
- Inline keyboards for approvals
- Push notifications
- Real-time alerts

**Commands**:
- `/start` - Start bot
- `/status` - System status
- `/positions` - Current positions
- `/kill` - Emergency stop

**Rate Limits**: 30 messages/second (per bot)

**Documentation**: [TELEGRAM_BOT_GUIDE.md](TELEGRAM_BOT_GUIDE.md)

**Status**: ✅ Primary user interface

---

### 5. yfinance (Historical Data) ✅ IMPLEMENTED

**Purpose**: Historical data backfill and validation

**Type**: REST API (unofficial Yahoo Finance)

**Authentication**: None

**Key Features**:
- Historical OHLCV data (2 years)
- Nifty 500 symbol list fetching
- Company information (sector, market cap)
- Batch processing with rate limiting
- Technical indicators calculation (29 indicators)

**Implementation**:
- `data_sources/yfinance_fetcher.py` - Main fetcher class
- `scripts/backfill_nifty500.py` - Backfill script with advanced options
- `data_sources/data_source_manager.py` - Orchestrator (yfinance only for now)

**Rate Limits**: None (but be respectful - batch processing recommended)

**Usage**: 
- Primary historical data source (until Shoonya/Upstox integrated)
- Nifty 500 backfill
- Data validation

**Status**: ✅ Implemented and operational

---

## Integration Priority

### Data Sources (Priority Order)

1. **Shoonya WebSocket** - Primary real-time data (Pending)
2. **Shoonya REST** - Primary historical/order data (Pending)
3. **Upstox REST** - Backup data source (Pending)
4. **yfinance** - Historical backfill/validation ✅ **Currently Active**

### LLM Services

1. **Local Ollama** - Primary (only) LLM service

### User Interface

1. **Telegram Bot** - Primary user interface

---

## API Status Monitoring

### Health Checks

```python
# Check API availability
- Shoonya: Session valid + WebSocket connected
- Upstox: Access token valid
- Ollama: Server running + models available
- Telegram: Bot token valid + API accessible
```

### Fallback Strategy

1. **Shoonya fails** → Use Upstox
2. **Upstox fails** → Use yfinance (historical only)
3. **Ollama fails** → System stops (no LLM = no trading)
4. **Telegram fails** → System continues (no user interaction)

---

## Configuration

All API credentials configured in `.env`:

```env
# Shoonya
SHOONYA_USER_ID=...
SHOONYA_PASSWORD=...
SHOONYA_TWO_FA=...
SHOONYA_VENDOR_CODE=...
SHOONYA_API_SECRET=...
SHOONYA_IMEI=...

# Upstox
UPSTOX_API_KEY=...
UPSTOX_API_SECRET=...
UPSTOX_ACCESS_TOKEN=...

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Error Handling

### Common Issues

1. **Shoonya Session Expired**
   - Solution: Re-authenticate (session valid ~24 hours)

2. **Upstox Token Expired**
   - Solution: Refresh token (expires daily at 3:30 AM IST)

3. **Ollama Server Down**
   - Solution: Start server (`ollama serve`)

4. **Telegram API Error**
   - Solution: Check bot token, verify API status

---

## Testing APIs

### Test Scripts

```bash
# Test Ollama
python scripts/test_ollama_connection.py

# Test yfinance backfill
python scripts/backfill_nifty500.py --update-recent 7

# Test Shoonya (pending)
python scripts/test_shoonya_connection.py

# Test Telegram (pending)
python scripts/test_telegram_bot.py
```

---

## Best Practices

1. **Always have fallbacks**: Shoonya → Upstox → yfinance
2. **Monitor API health**: Regular health checks
3. **Respect rate limits**: Implement request throttling
4. **Handle errors gracefully**: Don't crash on API failures
5. **Log all API calls**: For debugging and auditing

---

## Related Documentation

- [Shoonya API Guide](SHOONYA_API_GUIDE.md) - Complete Shoonya integration
- [Upstox API Guide](UPSTOX_API_GUIDE.md) - Complete Upstox integration
- [Ollama Local Setup](OLLAMA_LOCAL_SETUP.md) - Ollama installation and setup
- [Telegram Bot Guide](TELEGRAM_BOT_GUIDE.md) - Telegram bot setup and commands
- [Configuration Reference](04_CONFIGURATION_REFERENCE.md) - All configuration options

---

**Quick Reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common commands and tasks.
