# Quick Reference Guide

**Version**: 1.1  
**Last Updated**: January 2025  
**Status**: Phase 1 & Phase 2 Complete (Including Sentiment Analysis)

---

## 🚀 Quick Start Commands

### Initial Setup

```bash
# Create virtual environment
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Add sentiment analysis tables
python scripts/migrate_add_sentiment_tables.py

# (Optional) Download NLTK data for VADER sentiment
python -c "import nltk; nltk.download('vader_lexicon')"

# Test Ollama
python scripts/test_ollama_connection.py
```

### Ollama Setup

```bash
# Start Ollama server
ollama serve

# Pull required models
ollama pull deepseek-r1:7b
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b-instruct
ollama pull codegemma:7b
ollama pull gemma2:2b-instruct-q4_K_M
ollama pull phi3:mini

# Verify models
ollama list
```

---

## 📋 Common Commands

### Database

```bash
# Initialize database
python scripts/init_db.py

# Migrate database (add missing columns)
python scripts/migrate_add_sector_columns.py

# Add sentiment analysis tables
python scripts/migrate_add_sentiment_tables.py

# Backup database
cp data/trading.db backups/trading_$(date +%Y%m%d).db

# Restore database
cp backups/trading_20250115.db data/trading.db
```

### Historical Data Backfill

```bash
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

# Update recent 7 days with custom batch settings
python scripts/backfill_nifty500.py --update-recent 7 --batch-size 5 --batch-delay 1.0

# Show help
python scripts/backfill_nifty500.py --help
```

### Testing

```bash
# Test Ollama connection
python scripts/test_ollama_connection.py

# Test system health
python scripts/health_check.py

# Run tests
pytest tests/
```

### Running System

```bash
# Development mode
python main.py

# Production (PM2)
pm2 start main.py --name trading-bot

# Windows Service (NSSM)
nssm start TradingBot
```

---

## 🤖 Telegram Bot Commands

| Command | Purpose |
|---------|---------|
| `/start` | Initialize bot |
| `/status` | System status |
| `/positions` | Current positions |
| `/query <question>` | Ask questions |
| `/kill` | Emergency stop |
| `/resume` | Resume trading |

---

## 🔧 Configuration Quick Reference

### .env File Template

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_CHATBOT_MODEL=gemma2:2b-instruct-q4_K_M

# Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Shoonya
SHOONYA_USER_ID=your_user_id
SHOONYA_PASSWORD=your_password
SHOONYA_TWO_FA=your_2fa_key

# Database
DATABASE_URL=sqlite:///./data/trading.db
```

---

## 📊 Model Quick Reference

| Agent | Primary Model | Fallback |
|-------|---------------|----------|
| Strategy | `deepseek-r1:7b` | `qwen2.5:7b` |
| Database | `qwen2.5-coder:7b-instruct` | `codegemma:7b` |
| Chatbot | `gemma2:2b-instruct-q4_K_M` | `phi3:mini` |
| News Sentiment | `deepseek-r1:7b` | `qwen2.5:7b` |
| Guardian | `deepseek-r1:7b` | `qwen2.5:7b` |

---

## 🔗 API Endpoints Quick Reference

### Shoonya API
- **Base URL**: `https://api.shoonya.com/`
- **Auth**: Session-based + TOTP
- **Rate Limit**: 10 req/sec (quotes), 20 orders/sec

### Upstox API
- **Base URL**: `https://api.upstox.com/v2/`
- **Auth**: OAuth 2.0
- **Rate Limit**: 50 req/sec, 500 req/min

### Ollama (Local)
- **Base URL**: `http://localhost:11434`
- **Auth**: None
- **Rate Limit**: None

### Telegram Bot API
- **Base URL**: `https://api.telegram.org/bot<token>/`
- **Auth**: Bot token
- **Rate Limit**: 30 messages/sec

---

## 🐛 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Ollama not connecting | `ollama serve` |
| Model not found | `ollama pull <model_name>` |
| Database locked | Close other connections |
| Telegram not responding | Check bot token |
| Shoonya auth failed | Re-authenticate (24h expiry) |
| Sentiment tables missing | `python scripts/migrate_add_sentiment_tables.py` |
| News fetching fails | Check network, verify RSS URLs |
| Feedparser error | `pip install feedparser` |

---

## 📁 Important File Locations

| File/Directory | Purpose |
|----------------|---------|
| `.env` | Configuration |
| `data/trading.db` | Database |
| `logs/trading_app.log` | Logs |
| `config/settings.py` | Settings |
| `config/news_sources.py` | News source configuration |
| `data_sources/news_fetcher.py` | News fetching module |
| `database/repositories/sentiment_repo.py` | Sentiment repository |
| `docs/` | Documentation |

---

## 🔍 Common SQL Queries

```sql
-- Get latest market data
SELECT * FROM market_data_daily 
WHERE stock_id = 1 
ORDER BY date DESC LIMIT 1;

-- Find oversold stocks (RSI < 30)
SELECT s.symbol, md.rsi 
FROM stocks s
JOIN market_data_daily md ON s.id = md.stock_id
WHERE md.rsi < 30
ORDER BY md.rsi ASC;

-- Get active positions
SELECT * FROM portfolio 
WHERE quantity > 0;

-- Get latest sentiment for a stock
SELECT s.symbol, ss.overall_sentiment, ss.confidence, ss.date
FROM sentiment_scores ss
JOIN stocks s ON ss.stock_id = s.id
WHERE s.symbol = 'TCS'
ORDER BY ss.date DESC LIMIT 1;

-- Get recent news articles
SELECT title, source, published_date, category
FROM news_articles
ORDER BY published_date DESC
LIMIT 10;

-- Get stocks with positive sentiment
SELECT s.symbol, ss.overall_sentiment, ss.confidence
FROM sentiment_scores ss
JOIN stocks s ON ss.stock_id = s.id
WHERE ss.date = DATE('now')
AND ss.overall_sentiment > 0.5
ORDER BY ss.overall_sentiment DESC;
```

---

## 📝 Log Locations

```bash
# Main log
logs/trading_app.log

# View logs
tail -f logs/trading_app.log  # Linux/macOS
Get-Content logs/trading_app.log -Wait  # Windows PowerShell
```

---

## 🎯 Key Metrics

| Metric | Target |
|--------|--------|
| Signal Generation | < 10 seconds |
| Database Queries | < 100ms |
| API Response | < 5 seconds |
| System Uptime | 99% (market hours) |

---

## 📚 Documentation Quick Links

- [Quick Start](../QUICK_START.md) - Initial setup
- [Architecture](01_ARCHITECTURE_AND_DESIGN.md) - System design
- [Configuration](04_CONFIGURATION_REFERENCE.md) - All settings
- [Sentiment Analysis](09_SENTIMENT_ANALYSIS_SYSTEM.md) - Sentiment system guide
- [Free Sources](10_FREE_SENTIMENT_SOURCES.md) - Free news sources
- [Troubleshooting](06_TROUBLESHOOTING_AND_DEBUGGING.md) - Common issues
- [API Integration](API_INTEGRATION_SUMMARY.md) - All APIs
- [Telegram Bot](TELEGRAM_BOT_GUIDE.md) - Bot commands
- [Status & Changelog](11_STATUS_AND_CHANGELOG.md) - Current status

---

## 🔐 Security Checklist

- [ ] `.env` file not committed to git
- [ ] Bot token secured
- [ ] API keys encrypted
- [ ] Database backups automated
- [ ] Logs don't contain sensitive data

---

## ⚡ Performance Tips

1. **Ollama**: Use quantized models for faster inference
2. **Database**: Regular VACUUM for performance
3. **API Calls**: Batch requests when possible
4. **Model Loading**: Sequential loading (by design)
5. **Logs**: Rotate daily, clean old logs
6. **News Fetching**: Use rate limiting (15-30 min intervals)
7. **Sentiment Analysis**: Batch process articles (10-20 at a time)
8. **Article Cleanup**: Remove articles older than 30 days regularly

---

**For detailed information**: See the full documentation in `docs/` directory.
