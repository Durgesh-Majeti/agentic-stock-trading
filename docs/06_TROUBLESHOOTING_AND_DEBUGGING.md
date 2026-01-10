# Troubleshooting & Debugging Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Error Messages](#error-messages)
3. [Debugging Techniques](#debugging-techniques)
4. [Log Analysis](#log-analysis)
5. [Performance Issues](#performance-issues)
6. [API Issues](#api-issues)
7. [Database Issues](#database-issues)
8. [Agent Issues](#agent-issues)

---

## Common Issues

### Issue: Ollama Connection Failed

**Symptoms**:
- `ConnectionError` when calling LLM
- `Connection refused` errors

**Solutions**:
1. Make sure Ollama server is running: `ollama serve`
2. Verify `OLLAMA_BASE_URL` in `.env` (default: `http://localhost:11434`)
3. Test connection: `python scripts/test_ollama_connection.py`
4. Check if Ollama is installed: `ollama --version`
5. Verify models are pulled: `ollama list`

---

### Issue: Database Locked

**Symptoms**:
- `sqlite3.OperationalError: database is locked`
- Queries timeout

**Solutions**:
1. Ensure only one process accesses database
2. Check for long-running transactions
3. Close all database connections properly
4. Use connection pooling
5. Restart application

---

### Issue: Telegram Bot Not Responding

**Symptoms**:
- Bot doesn't respond to commands
- Webhook errors

**Solutions**:
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check bot is running: `python -c "from telegram import Bot; Bot(token='YOUR_TOKEN').get_me()"`
3. Check network connectivity
4. Verify bot is not blocked
5. Restart bot process

---

### Issue: Shoonya API Authentication Failed

**Symptoms**:
- `401 Unauthorized`
- Login fails

**Solutions**:
1. Verify all credentials in `.env`
2. Check TOTP is current (30-second validity)
3. Verify vendor code format: `CLIENTCODE_U`
4. Check IMEI/MAC address
5. Test login: `python scripts/test_shoonya_connection.py`

---

### Issue: No Signals Generated

**Symptoms**:
- No trade signals in database
- Strategy agent returns HOLD

**Solutions**:
1. Check confidence threshold (default 75%)
2. Verify market data is fresh
3. Check database has recent data
4. Review strategy agent logs
5. Test with known good symbol
6. Check if sentiment data is available (if using sentiment analysis)

---

### Issue: News Fetching Fails

**Symptoms**:
- No articles fetched from RSS feeds
- `feedparser` errors
- Empty article lists

**Solutions**:
1. Check network connectivity
2. Validate RSS feed URLs: `python scripts/validate_rss_urls.py`
3. Check User-Agent headers are set correctly
4. Verify feedparser is installed: `pip install feedparser`
5. Test RSS feed manually: `python -c "import feedparser; print(feedparser.parse('URL'))"`
6. Check for rate limiting (wait 15-30 minutes between fetches)
7. Review news fetcher logs for specific errors
8. Check for timezone errors (all datetimes should be naive UTC)
9. Verify BSE RSS feed URL: `https://www.bseindia.com/rssxml/Corporate_Announcements.xml`
10. Check source status: Use `get_all_sources_status()` method

---

### Issue: Sentiment Analysis Fails

**Symptoms**:
- Sentiment scores not generated
- LLM errors during sentiment analysis
- Empty sentiment scores in database

**Solutions**:
1. Verify Ollama is running: `ollama serve`
2. Check DeepSeek R1 7B model is pulled: `ollama list`
3. Verify model is accessible: `python scripts/test_ollama_connection.py`
4. Check if articles are stored in database
5. Review sentiment repository logs
6. Verify sentiment tables exist: `python scripts/migrate_add_sentiment_tables.py`

---

### Issue: Sentiment Tables Missing

**Symptoms**:
- `Table 'news_articles' doesn't exist` errors
- Sentiment repository operations fail

**Solutions**:
1. Run migration script: `python scripts/migrate_add_sentiment_tables.py`
2. Verify database file exists: `data/trading.db`
3. Check migration script output for errors
4. Verify tables were created: Check database with SQLite browser
5. Re-run migration if needed (script handles existing tables)

---

## Error Messages

### Database Errors

**Error**: `no such table: market_data_daily`
**Solution**: Run `python scripts/init_db.py`

**Error**: `UNIQUE constraint failed`
**Solution**: Data already exists, skip or update

**Error**: `database disk image is malformed`
**Solution**: Restore from backup

---

### API Errors

**Error**: `Rate limit exceeded`
**Solution**: Implement rate limiting, wait before retry

**Error**: `Invalid API key`
**Solution**: Check credentials in `.env`

**Error**: `Connection timeout`
**Solution**: Check network, retry with exponential backoff

---

### Agent Errors

**Error**: `INVALID_QUERY` from Librarian
**Solution**: Simplify query, check schema

**Error**: `JSON decode error` from Strategy
**Solution**: Check LLM response format, add retry logic

---

## Debugging Techniques

### Enable Debug Logging

```python
# In .env
LOG_LEVEL=DEBUG
```

### Add Debug Prints

```python
from loguru import logger

logger.debug(f"Variable value: {variable}")
logger.info(f"Processing: {data}")
logger.warning(f"Potential issue: {issue}")
logger.error(f"Error occurred: {error}")
```

### Use Python Debugger

```python
import pdb

# Set breakpoint
pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

---

## Log Analysis

### Key Log Locations

- **Main Log**: `logs/trading_app.log`
- **Agent Logs**: `logs/agents/`
- **Error Logs**: `logs/errors/`

### Log Patterns

**Successful Signal**:
```
INFO | Strategy Specialist | Signal generated: BUY TCS @ 3245.5 (82% confidence)
```

**Error Pattern**:
```
ERROR | Data Scraper | Shoonya API error: Connection timeout
WARNING | Data Scraper | Falling back to Upstox
```

### Search Logs

```bash
# Find errors
grep "ERROR" logs/trading_app.log

# Find specific symbol
grep "TCS" logs/trading_app.log

# Find today's logs
grep "$(date +%Y-%m-%d)" logs/trading_app.log
```

---

## Performance Issues

### Slow Queries

**Symptoms**: Database queries take > 1 second

**Solutions**:
1. Check indexes are used: `EXPLAIN QUERY PLAN`
2. Optimize query structure
3. Add missing indexes
4. Limit result sets

### High Memory Usage

**Symptoms**: System runs out of memory

**Solutions**:
1. Load models sequentially (not parallel)
2. Clear model cache periodically
3. Reduce batch sizes
4. Monitor memory usage

### Slow Signal Generation

**Symptoms**: Signals take > 30 seconds

**Solutions**:
1. Check LLM response times
2. Optimize database queries
3. Cache frequently used data
4. Reduce number of candidates

---

## API Issues

### Shoonya API

**Issue**: WebSocket disconnects frequently
**Solution**: Implement reconnection logic

**Issue**: Rate limit errors
**Solution**: Implement rate limiting, batch requests

### Upstox API

**Issue**: Token expired
**Solution**: Implement token refresh logic

**Issue**: 429 Too Many Requests
**Solution**: Reduce request frequency

### Local Ollama

**Issue**: Model not found
**Solution**: Pull model with `ollama pull <model_name>`

**Issue**: Server not running
**Solution**: Start Ollama server with `ollama serve`

**Issue**: Connection refused
**Solution**: Check if server is running, verify OLLAMA_BASE_URL

---

## Database Issues

### Database Corruption

**Symptoms**: Queries fail, data inconsistent

**Solutions**:
1. Restore from backup
2. Run `VACUUM`
3. Check disk space
4. Verify file permissions

### Missing Data

**Symptoms**: Expected data not in database

**Solutions**:
1. Check data collection logs
2. Verify backfill completed
3. Check data validation rules
4. Review error logs

---

## Agent Issues

### Librarian Issues

**Issue**: Generates invalid SQL
**Solution**: 
- Simplify query
- Check schema knowledge
- Use fallback model
- Add SQL validation

### Strategy Issues

**Issue**: Low confidence signals
**Solution**:
- Check input data quality
- Review market conditions
- Adjust confidence threshold
- Check model performance

### Scraper Issues

**Issue**: Stale data
**Solution**:
- Check API connectivity
- Verify data freshness checks
- Switch to backup source
- Review rate limiting

---

## Quick Reference

### Test Commands

```bash
# Test Ollama
python scripts/test_ollama_connection.py

# Test Database
python scripts/test_database.py

# Test Agents
python scripts/test_agents.py

# Health Check
python scripts/health_check.py

# Validate RSS Feeds
python scripts/validate_rss_urls.py
```

### Reset Procedures

```bash
# Reset Database (WARNING: Deletes all data)
rm data/trading.db
python scripts/init_db.py

# Clear Logs
rm -rf logs/*

# Reset Configuration
cp .env.example .env
# Edit .env with your credentials
```

---

**Next**: `07_TESTING_AND_QUALITY_ASSURANCE.md`
