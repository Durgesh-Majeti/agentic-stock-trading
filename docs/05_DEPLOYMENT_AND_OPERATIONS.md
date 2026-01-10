# Deployment & Operations Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Initial Setup](#initial-setup)
4. [Running the System](#running-the-system)
5. [Monitoring](#monitoring)
6. [Backup & Recovery](#backup--recovery)
7. [Maintenance](#maintenance)
8. [Production Checklist](#production-checklist)

---

## Prerequisites

### System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.12 (recommended)
- **RAM**: 8GB minimum
- **Storage**: 5GB free space
- **Network**: Stable internet connection

### Required Accounts

1. **Ollama**: Local installation (no account needed)
2. **Telegram**: Bot token
3. **Shoonya**: Trading account + API key
4. **Upstox**: Trading account + API key (optional)

---

## Installation Steps

### Step 1: Clone/Download Project

```bash
cd "D:\Python Projects\Agentic Stock trading"
```

### Step 2: Create Virtual Environment

```powershell
# Windows PowerShell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
python3.12 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install and Setup Ollama

1. **Download Ollama**: https://ollama.com/download
   - Windows: `winget install Ollama.Ollama`
   - Or download installer
2. **Start Ollama Server**: 
   ```bash
   ollama serve
   ```
3. **Pull Required Models**:
   ```bash
   ollama pull deepseek-r1:7b
   ollama pull qwen2.5:7b
   ollama pull qwen2.5-coder:7b-instruct
   ollama pull codegemma:7b
   ollama pull gemma2:2b-instruct-q4_K_M
   ollama pull phi3:mini
   ```

### Step 5: Configure Environment

1. Copy `.env.example` to `.env`
2. Fill in all required credentials
3. Verify all settings

### Step 6: Initialize Database

```bash
# Initialize core database tables
python scripts/init_db.py

# Add sentiment analysis tables (required for sentiment features)
python scripts/migrate_add_sentiment_tables.py
```

**Note**: The sentiment tables migration is required if you plan to use sentiment analysis features. It creates:
- `news_articles` table
- `sentiment_scores` table
- `macro_stock_sentiment` table
- `news_sources` table

### Step 7: (Optional) Setup Sentiment Analysis Tools

If you want to use FinBERT or VADER for faster sentiment analysis on simple articles:

```bash
# For VADER sentiment (lightweight)
python -c "import nltk; nltk.download('vader_lexicon')"

# For FinBERT (requires ~2GB download)
# FinBERT will be automatically downloaded on first use if transformers is installed
# pip install transformers torch  # Already in requirements.txt (optional)
```

**Note**: DeepSeek R1 7B (already in your system) is the primary sentiment analyzer. FinBERT and VADER are optional optimizations.

### Step 8: Test Connections

```bash
# Test Ollama (make sure server is running)
python scripts/test_ollama_connection.py

# Test Shoonya (if implemented)
python scripts/test_shoonya_connection.py
```

---

## Initial Setup

### Database Backfill

```bash
# Backfill Nifty 500 historical data
python scripts/backfill_nifty500.py
```

**Expected Time**: 2-4 hours for 2 years of data

### Verify Setup

```bash
# Check database
python scripts/verify_database.py

# Verify sentiment tables (if using sentiment)
python -c "from database.session import get_session; from database.models import NewsArticle; s = next(get_session()); print(f'Sentiment tables OK: {s.query(NewsArticle).count()} articles')"

# Check agents
python scripts/test_agents.py
```

---

## Running the System

### Development Mode

```bash
# Start main orchestrator
python main.py
```

### Production Mode

```bash
# Use process manager (PM2, systemd, etc.)
pm2 start main.py --name trading-bot
```

### Windows Service

```powershell
# Create service
nssm install TradingBot "D:\Python Projects\Agentic Stock trading\venv\Scripts\python.exe" "D:\Python Projects\Agentic Stock trading\main.py"
nssm start TradingBot
```

---

## Monitoring

### Log Files

- **Location**: `logs/trading_app.log`
- **Rotation**: Daily
- **Retention**: 30 days

### Key Metrics

- **Signal Generation Rate**: 3-5 signals/day
- **Order Execution Rate**: Based on approvals
- **News Articles Fetched**: 500-1000 articles/day (if using sentiment)
- **Sentiment Scores Generated**: 500 stocks/day (if using sentiment)
- **API Response Times**: < 5 seconds
- **Database Query Times**: < 100ms
- **System Uptime**: 99% during market hours

### Health Checks

```python
# scripts/health_check.py
def check_system_health():
    """Check system health."""
    checks = {
        "database": check_database(),
        "ollama": check_ollama(),
        "shoonya": check_shoonya(),
        "telegram": check_telegram(),
        "news_sources": check_news_sources(),  # If using sentiment
        "sentiment_tables": check_sentiment_tables()  # If using sentiment
    }
    return checks
```

---

## Backup & Recovery

### Automated Backups

```bash
# Daily backup script
python scripts/backup_database.py
```

### Manual Backup

```bash
# Copy database
cp data/trading.db backups/trading_$(date +%Y%m%d).db
```

### Recovery

```bash
# Restore from backup
cp backups/trading_20250115.db data/trading.db
```

---

## Maintenance

### Daily Tasks

- Check logs for errors
- Verify backups
- Monitor API usage
- Review trades

### Weekly Tasks

- Database maintenance (VACUUM)
- Clean old logs
- Clean old news articles (30+ days) - if using sentiment
- Review performance metrics
- Update dependencies

### Monthly Tasks

- Full system backup
- Security audit
- Performance review
- Documentation update
- News article cleanup (30+ days old)
- Sentiment data review

---

## Production Checklist

### Pre-Deployment

- [ ] All credentials configured
- [ ] Database initialized
- [ ] Sentiment analysis tables created (`migrate_add_sentiment_tables.py`)
- [ ] Historical data backfilled
- [ ] News sources configured and tested
- [ ] All tests passing
- [ ] Logging configured
- [ ] Backups automated
- [ ] Monitoring setup
- [ ] Error handling tested

### Deployment

- [ ] System running in paper mode
- [ ] All agents operational
- [ ] Telegram bot responding
- [ ] Data collection working
- [ ] News fetching working (if using sentiment)
- [ ] Sentiment analysis working (if using sentiment)
- [ ] Signal generation working
- [ ] Order execution tested (paper)

### Post-Deployment

- [ ] Monitor for 24 hours
- [ ] Verify all alerts working
- [ ] Check performance metrics
- [ ] Review logs for errors
- [ ] Test emergency procedures

---

**Next Documents**:
- `06_TROUBLESHOOTING_AND_DEBUGGING.md` - Troubleshooting guide
- `07_TESTING_AND_QUALITY_ASSURANCE.md` - Testing guide
