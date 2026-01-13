# Agentic AI Stock Trading App for Indian Markets

**Version**: 1.4.0  
**Last Updated**: January 2025

A comprehensive agentic AI application for Indian stock trading with dashboard, Telegram bot, and multi-agent analysis system using local Ollama models.

## 🎯 Features

- 🤖 **5-Agent System**: Strategy Specialist, Database Librarian, Data Scraper, Telegram Assistant, News Sentiment Analyst
- 📊 **Real-time Dashboard**: Streamlit dashboard with Plotly charts for portfolio, orders, trades
- 💬 **Telegram Bot**: Mobile trade approvals and control
- 📈 **Multi-Source Analysis**: Fundamental, Technical (29 indicators), and Sentiment analysis
- 📰 **News Sentiment Analysis**: Multi-source news aggregation with sentiment scoring
- 💾 **Centralized Database**: SQLite database as central point for all agents
- 🧠 **Specialized AI Models**: 
  - DeepSeek R1 7B for trading decisions and sentiment analysis (thinking mode)
  - Qwen2.5 Coder for SQL generation
  - Gemma2 for chatbot interactions
- 💰 **Budget-Friendly**: Free/budget-friendly APIs, local database, and free news sources

## 🏗️ Architecture

### Agents (CrewAI)

1. **Strategy Specialist** - Swing trading expert, generates trade recommendations with sentiment integration
2. **Database Librarian** - Natural language to SQL translator
3. **Data Scraper** - Multi-source data collection (Shoonya WebSocket, Upstox, yfinance)
4. **Telegram Assistant** - Human interface for approvals and queries
5. **News Sentiment Analyst** - News aggregation and sentiment analysis from 10+ free sources

### Resilience Layer (+1)

Non-agent Python cron jobs:
- Heartbeat monitoring
- Stop-loss monitoring
- Portfolio heat checking

## 🛠️ Tech Stack

- **Framework**: CrewAI for multi-agent orchestration
- **LLM**: Local Ollama (deepseek-r1:7b, qwen2.5-coder:7b-instruct, gemma2:2b-instruct-q4_K_M)
- **Dashboard**: Streamlit + Plotly
- **Database**: SQLite with SQLAlchemy
- **Trading API**: Shoonya WebSocket
- **Telegram**: python-telegram-bot
- **Analysis**: 29 Technical Indicators, Sentiment Analysis

## 📦 Installation

### Prerequisites

**Python 3.12 is recommended** for best compatibility. Python 3.13 may have package compatibility issues.

1. **Install Python 3.12**:
   - Download from: https://www.python.org/downloads/release/python-31211/
   - **Important**: Check "Add Python 3.12 to PATH" during installation
   - See `PYTHON_INSTALLATION_GUIDE.md` for detailed instructions

2. **Navigate to project**:
```bash
cd "D:\Python Projects\Agentic Stock trading"
```

3. **Create virtual environment with Python 3.12**:
```bash
py -3.12 -m venv venv
venv\Scripts\activate  # Windows PowerShell
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**Note**: The Shoonya API is installed from GitLab. If you encounter issues, you can install it separately:
```bash
pip install git+https://gitlab.com/algo2t/shoonya.git
```

5. **Install and Setup Ollama**:
   - Download Ollama from: https://ollama.com/download
   - Or use: `winget install Ollama.Ollama` (Windows)
   - Start Ollama server: `ollama serve`
   - Pull required models (see QUICK_START.md for list)

6. **Configure environment**:
   - Create a `.env` file in the project root
   - See `QUICK_START.md` for the complete `.env` template
   - Add your Telegram bot token and Shoonya credentials

7. **Initialize database**:
```bash
python scripts/init_db.py
python scripts/migrate_add_sentiment_tables.py
```

8. **Test Ollama connection**:
```bash
python scripts/test_ollama_connection.py
```

9. **(Optional) Setup sentiment analysis tools**:
```bash
# For VADER sentiment (if using)
python -c "import nltk; nltk.download('vader_lexicon')"
```

## 🚀 Running the Application

**Note**: The main orchestrator, dashboard, and Telegram bot are currently under development. The core infrastructure and historical data backfill are ready.

### Current Status

✅ **Phase 1: Foundation & Infrastructure** (Complete)
- Database schema and repositories
- Local Ollama service integration
- Configuration management
- Technical indicators calculation (29 indicators)
- Service layer (trading, approval, analysis, notification)
- Database migration scripts

✅ **Phase 2: Data Sources Integration** (Complete)
- yfinance integration with Nifty 500 support
- News sources integration (12 RSS feeds)
- Data source orchestrator
- Historical data backfill script with advanced options

✅ **Phase 3: Agent Implementation** (67% Complete - 4/6 agents)
- ✅ Base Agent Framework
- ✅ Database Librarian (NL to SQL)
- ✅ Data Scraper (multi-source)
- ✅ Strategy Specialist (all 10 improvements)
- ✅ News Sentiment Analyst (hybrid FinBERT + LLM)
- ⏳ Telegram Assistant (pending)
- ⏳ Portfolio Guardian (pending)

✅ **Phase 5: Orchestration** (Complete)
- Complete orchestrator with all 10 improvements
- All 4 agents integrated
- Agent-specific timeouts
- Workflow registry and contract validation

🚧 **In Development:**
- Telegram Assistant agent
- Portfolio Guardian agent
- Streamlit dashboard
- Shoonya API integration (Phase 2.1)
- Upstox API integration (Phase 2.2)
- Resilience layer (cron jobs)

### Quick Start - Historical Data Backfill

```bash
# Standard backfill (incremental, 2 years)
python scripts/backfill_nifty500.py

# Update only last 30 days
python scripts/backfill_nifty500.py --update-recent 30

# Force refresh all data
python scripts/backfill_nifty500.py --force-refresh

# Show all options
python scripts/backfill_nifty500.py --help
```

### Quick Start - News & Sentiment

```bash
# Test news fetching
python -c "from data_sources.news_fetcher import NewsFetcher; f = NewsFetcher(); articles = f.fetch_all_sources(); print(f'Fetched {len(articles)} articles')"

# Check sentiment tables
python -c "from database.session import get_session; from database.models import NewsArticle; s = next(get_session()); print(f'Articles in DB: {s.query(NewsArticle).count()}')"
```

### Quick Start

See `QUICK_START.md` for detailed setup instructions.

## ⚙️ Configuration

Edit `.env` file with:

- **Ollama Local**: Base URL (default: http://localhost:11434) and model names
- **Telegram Bot**: Bot token from @BotFather
- **Shoonya API**: Trading account credentials
- **Trading Settings**: Risk parameters, watchlist, etc.

## 📊 Database Schema

- `stocks` - Stock master
- `market_data_daily` - Daily OHLCV + 29 indicators (2 years)
- `market_data_intraday` - Intraday data (60 days, 1h bars)
- `screening_signals` - Agent-generated signals
- `agent_decisions` - Audit trail of agent decisions
- `orders` - Orders with approval workflow
- `trades` - Executed trades
- `portfolio` - Current holdings
- `user_actions` - User action audit trail
- `performance_metrics` - Performance tracking
- `tax_ledger` - Tax compliance
- `news_articles` - News articles from multiple sources (30-day retention)
- `sentiment_scores` - Daily aggregated sentiment per stock
- `macro_stock_sentiment` - Macro news to stock sentiment mapping
- `news_sources` - News source configuration

## 🔄 Workflow

1. **Data Collection**: Data Scraper collects real-time data via Shoonya WebSocket
2. **Analysis**: Strategy Specialist analyzes data and generates trade recommendations
3. **Approval**: Orders require approval via Telegram or Dashboard
4. **Execution**: Approved orders executed via Shoonya API
5. **Tracking**: All trades tracked in database with P&L calculation

## 🛡️ Safety Features

- **Approval Workflow**: Every trade requires manual approval
- **Risk Management**: Position sizing, stop-loss, portfolio heat limits
- **Resilience Layer**: Automatic monitoring and safeguards
- **Ollama Downtime**: Trading stops, dashboard remains available for manual trading

## 📝 Notes

- This is for educational purposes
- Trading involves risk - always do your own research
- Start with paper trading
- Test thoroughly before live trading

## 🔧 Troubleshooting

- **Ollama not available**: Make sure Ollama server is running (`ollama serve`)
- **Models not found**: Pull required models (`ollama pull <model_name>`)
- **Database errors**: Run `python scripts/init_db.py`
- **Sentiment tables missing**: Run `python scripts/migrate_add_sentiment_tables.py`
- **Shoonya connection**: Verify credentials in `.env`
- **News fetching errors**: Check network connection and RSS feed URLs

## 📄 License

Educational use only.
