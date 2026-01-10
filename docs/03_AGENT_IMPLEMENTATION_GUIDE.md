# Agent Implementation Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [Agent #1: Database Librarian](#agent-1-database-librarian)
4. [Agent #2: Data Scraper](#agent-2-data-scraper)
5. [Agent #3: Strategy Specialist](#agent-3-strategy-specialist)
6. [Agent #4: Telegram Assistant](#agent-4-telegram-assistant)
7. [Agent #5: News Sentiment Analyst](#agent-5-news-sentiment-analyst)
8. [Agent #6: Portfolio Guardian](#agent-6-portfolio-guardian)
9. [Common Patterns](#common-patterns)
10. [Error Handling](#error-handling)
11. [Testing](#testing)

---

## Overview

### Agent Responsibilities

Each agent has a **single, well-defined responsibility**:
- **Librarian**: NL → SQL translation
- **Scraper**: Multi-source data collection
- **Strategy**: Trade signal generation
- **Telegram**: User interface
- **News Sentiment**: News aggregation and sentiment analysis
- **Guardian**: Portfolio monitoring

### Communication Pattern

Agents communicate via:
- **Database**: Shared SQLite database
- **Messages**: Structured JSON messages
- **Events**: Event-driven architecture
- **No Direct Calls**: Agents don't call each other directly

---

## Agent Architecture

### Design Principles

All agents in the system follow a consistent architecture pattern that ensures:

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Consistent Interface**: All agents implement the same base interface
3. **LLM Abstraction**: Agents don't directly manage LLM connections - handled by OllamaService
4. **Decision Logging**: All agent decisions are automatically logged for audit trails
5. **Error Handling**: Base class provides common error handling patterns

### Base Agent Class

The `BaseAgent` class provides the foundation for all agents. It handles common functionality like LLM initialization, decision logging, and provides the abstract interface that all agents must implement.

**Key Responsibilities**:
- **LLM Management**: Automatically initializes the appropriate LLM model based on agent role
- **Decision Logging**: Provides a standardized way to log all agent decisions to the database
- **Abstract Interface**: Defines the `process()` method that all agents must implement

**Model Role Mapping**:
- `"strategy"` → Uses DeepSeek R1 7B for complex reasoning tasks
- `"database"` → Uses Qwen2.5 Coder for SQL generation
- `"chatbot"` → Uses Gemma2 for natural language interaction

The base class ensures that agents don't need to worry about LLM connection management or decision logging - these are handled automatically.

```python
# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger
from services.ollama_service import OllamaService

class BaseAgent(ABC):
    """Base class for all agents.
    
    Provides common functionality:
    - LLM initialization based on role
    - Decision logging to database
    - Error handling patterns
    """
    
    def __init__(self, name: str, model_role: str):
        self.name = name
        self.ollama_service = OllamaService()
        self.llm = None
        self.model_role = model_role
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM for this agent based on role.
        
        Different agents use different models optimized for their tasks:
        - Strategy agents need reasoning capabilities
        - Database agents need code generation
        - Chatbot agents need natural language understanding
        """
        if self.model_role == "strategy":
            self.llm = self.ollama_service.get_strategy_llm()
        elif self.model_role == "database":
            self.llm = self.ollama_service.get_database_llm()
        elif self.model_role == "chatbot":
            self.llm = self.ollama_service.get_chatbot_llm()
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output.
        
        This is the main entry point for all agents. Each agent
        implements this method with its specific logic.
        """
        pass
    
    def log_decision(self, decision_type: str, reasoning: str, 
                    input_data: Dict, output_data: Dict):
        """Log agent decision to database for audit trail.
        
        This method automatically logs all agent decisions, including:
        - What decision was made
        - Why it was made (reasoning)
        - Input data that led to the decision
        - Output data from the decision
        
        This is critical for debugging, compliance, and performance analysis.
        """
        from database.repositories.analysis_repo import AnalysisRepository
        from database.session import get_session
        
        repo = AnalysisRepository(get_session())
        repo.create_agent_decision(
            agent_name=self.name,
            decision_type=decision_type,
            reasoning=reasoning,
            input_data=input_data,
            output_data=output_data
        )
```

**Usage Pattern**: All agents inherit from `BaseAgent` and implement the `process()` method. The base class handles all the common functionality, allowing agents to focus on their specific logic.

---

## Agent #1: Database Librarian

### Purpose and Responsibilities

The Database Librarian agent acts as a natural language interface to the trading database. It translates user queries in plain English into optimized SQL queries, executes them safely, and returns structured results.

**Key Capabilities**:
- **Natural Language to SQL**: Converts queries like "Show me oversold stocks today" into valid SQLite queries
- **Schema Awareness**: Understands the complete database schema including all tables, columns, and relationships
- **Query Safety**: Validates and sanitizes queries to prevent SQL injection
- **Result Formatting**: Returns results in structured JSON format for easy consumption

**Why This Agent Exists**: Instead of requiring users or other agents to write SQL directly, the Database Librarian provides an intelligent interface that understands context and can generate complex queries from simple natural language requests.

### Implementation Approach

The agent uses a two-step process:
1. **Translation**: Uses the LLM (Qwen2.5 Coder) to convert natural language to SQL
2. **Execution**: Safely executes the SQL query and formats results

The agent maintains awareness of the database schema, which is provided as context to the LLM. This allows it to generate accurate queries that reference the correct tables and columns.

```python
# agents/database_librarian.py
from agents.base_agent import BaseAgent
from database.session import get_session
import sqlite3
import json
from typing import List, Dict, Any

class DatabaseLibrarian(BaseAgent):
    """Natural language to SQL translator."""
    
    def __init__(self):
        super().__init__("database_librarian", "database")
        self.db_path = "data/trading.db"
        self.schema = self._load_schema()
    
    def _load_schema(self) -> str:
        """Load database schema for context."""
        return """
        Tables:
        - stocks(id, symbol, name, exchange, is_active)
        - market_data_daily(id, stock_id, date, open, high, low, close, volume, rsi, macd, ...)
        - market_data_intraday(id, stock_id, timestamp, open, high, low, close, volume)
        - screening_signals(id, stock_id, signal_type, confidence_score, entry_price, ...)
        - trades(id, stock_id, buy_sell, quantity, entry_price, exit_price, pnl, ...)
        - portfolio(id, stock_id, quantity, avg_price, current_price, unrealized_pnl)
        - nifty500_sectors(symbol, name, sector, industry)
        """
    
    def translate(self, natural_language_query: str) -> str:
        """Convert natural language to SQL."""
        prompt = f"""You are a SQLite expert for a trading database.

SCHEMA:
{self.schema}

User Query: "{natural_language_query}"

Generate ONLY the SQL query. No explanations, no markdown, just SQL.
Use parameterized queries for safety.
Return only valid SQLite syntax.

SQL:"""
        
        try:
            sql = self.llm.invoke(prompt)
            # Clean up response
            sql = sql.strip()
            sql = sql.replace("```sql", "").replace("```", "")
            sql = sql.strip()
            
            # Log decision
            self.log_decision(
                decision_type="SQL_QUERY",
                reasoning=f"Translated: {natural_language_query}",
                input_data={"query": natural_language_query},
                output_data={"sql": sql}
            )
            
            return sql
        except Exception as e:
            logger.error(f"SQL translation error: {e}")
            return "INVALID_QUERY"
    
    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """Safely execute SQL query."""
        if sql == "INVALID_QUERY":
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # Convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in results]
            
            conn.close()
            return data
            
        except sqlite3.Error as e:
            logger.error(f"SQL execution error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process natural language query."""
        query = input_data.get("query", "")
        sql = self.translate(query)
        results = self.execute(sql)
        
        return {
            "sql": sql,
            "results": results,
            "count": len(results)
        }
```

### Example Usage

```python
librarian = DatabaseLibrarian()

# Example 1: Oversold RSI stocks
result = librarian.process({
    "query": "Show me oversold RSI stocks today"
})
# Returns: SQL + results

# Example 2: IT sector gainers
result = librarian.process({
    "query": "Find IT sector stocks with MACD crossover"
})
```

---

## Agent #2: Data Scraper

### Implementation

```python
# agents/data_scraper.py
from agents.base_agent import BaseAgent
from data_sources.shoonya_scraper import ShoonyaScraper
from data_sources.upstox_scraper import UpstoxScraper
from data_sources.yfinance_scraper import YFinanceScraper
from database.repositories.market_data_repo import MarketDataRepository
from database.session import get_session
from utils.technical_indicators import TechnicalIndicators
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class DataScraper(BaseAgent):
    """Multi-source data orchestrator."""
    
    def __init__(self):
        super().__init__("data_scraper", None)  # No LLM needed
        self.shoonya = ShoonyaScraper()
        self.upstox = UpstoxScraper()
        self.yfinance = YFinanceScraper()
        self.repo = MarketDataRepository(get_session())
        self.indicators = TechnicalIndicators()
        self.primary_source = "shoonya"
    
    def fetch_live_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch live data from primary source (Shoonya)."""
        try:
            data = self.shoonya.get_quote(symbol)
            
            # Validate data
            if self._validate_data(data):
                return {
                    "symbol": symbol,
                    "data": data,
                    "source": "shoonya",
                    "valid": True,
                    "timestamp": datetime.now()
                }
            else:
                # Try backup
                return self._fetch_backup(symbol)
                
        except Exception as e:
            logger.error(f"Shoonya fetch error: {e}")
            return self._fetch_backup(symbol)
    
    def _fetch_backup(self, symbol: str) -> Dict[str, Any]:
        """Fetch from backup source (Upstox)."""
        try:
            data = self.upstox.get_quote(symbol)
            
            if self._validate_data(data):
                return {
                    "symbol": symbol,
                    "data": data,
                    "source": "upstox",
                    "valid": True,
                    "timestamp": datetime.now()
                }
        except Exception as e:
            logger.error(f"Upstox fetch error: {e}")
        
        return {
            "symbol": symbol,
            "data": None,
            "source": None,
            "valid": False,
            "timestamp": datetime.now()
        }
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data quality."""
        if not data:
            return False
        
        # Price sanity check
        current = data.get("ltp", 0)
        prev_close = data.get("prev_close", current)
        
        if abs(current - prev_close) / prev_close > 0.10:  # 10% deviation
            logger.warning(f"Price sanity check failed: {current} vs {prev_close}")
            return False
        
        # Freshness check
        timestamp = data.get("timestamp")
        if timestamp:
            age = datetime.now() - timestamp
            if age > timedelta(minutes=2):
                logger.warning(f"Data too stale: {age}")
                return False
        
        return True
    
    def fetch_historical_data(self, symbol: str, days: int = 730) -> List[Dict[str, Any]]:
        """Fetch historical data from yfinance."""
        try:
            data = self.yfinance.get_historical_data(symbol, days=days)
            return data
        except Exception as e:
            logger.error(f"Historical data fetch error: {e}")
            return []
    
    def store_daily_data(self, symbol: str, data: Dict[str, Any]):
        """Store daily data with indicators."""
        try:
            # Get stock
            stock = self.repo.get_stock_by_symbol(symbol)
            if not stock:
                stock = self.repo.create_stock(symbol, symbol, "NSE")
            
            # Calculate indicators
            indicators = self.indicators.calculate_all_indicators(data)
            
            # Store
            self.repo.add_daily_data(
                stock_id=stock.id,
                date=data["date"],
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                volume=data["volume"],
                **indicators
            )
        except Exception as e:
            logger.error(f"Store data error: {e}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data fetch request."""
        symbol = input_data.get("symbol")
        data_type = input_data.get("type", "live")  # live or historical
        
        if data_type == "live":
            return self.fetch_live_data(symbol)
        else:
            return {
                "symbol": symbol,
                "data": self.fetch_historical_data(symbol),
                "type": "historical"
            }
```

---

## Agent #3: Strategy Specialist

### Purpose and Responsibilities

The Strategy Specialist is the core decision-making agent of the trading system. It analyzes technical indicators, market data, and sentiment to generate high-conviction trade recommendations.

**Key Capabilities**:
- **Technical Analysis**: Analyzes 29 technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Pattern Recognition**: Identifies swing trading setups (oversold reversals, breakouts, pullbacks, trend continuations)
- **Risk Management**: Calculates appropriate stop losses (2%), targets (4%), and position sizes
- **Confidence Scoring**: Assigns confidence scores (0-100%) to each trade signal
- **Sentiment Integration**: Incorporates news sentiment data to enhance decision-making

**Decision Process**: The agent requires multiple confirmations (2+) before generating a signal. This reduces false positives. It also considers portfolio-level constraints like sector exposure limits.

**Output Format**: All signals are returned as structured JSON with entry price, stop loss, target, confidence, and reasoning. This ensures consistency and makes it easy for other components to process the signals.

### Implementation Approach

The Strategy Specialist uses DeepSeek R1 7B for its reasoning capabilities. The agent:
1. Receives market data (OHLCV + 29 indicators) and sentiment data
2. Builds a comprehensive prompt with trading rules and setup patterns
3. Uses the LLM to analyze and generate a trade signal
4. Validates the signal (confidence must be >75%)
5. Logs the decision for audit trail

The prompt engineering is critical here - the agent is given specific trading rules, setup patterns, and risk parameters to ensure it generates signals that align with the swing trading strategy.

```python
# agents/strategy_specialist.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class StrategySpecialist(BaseAgent):
    """Swing trading signal generator."""
    
    def __init__(self):
        super().__init__("strategy_specialist", "strategy")
        self.min_confidence = 75.0
        self.max_risk_per_trade = 0.05  # 5% portfolio risk
    
    def analyze(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symbol and generate trade signal."""
        prompt = self._build_prompt(symbol_data)
        
        try:
            response = self.llm.invoke(prompt)
            signal = self._parse_response(response)
            
            # Validate signal
            if signal.get("confidence", 0) < self.min_confidence:
                signal["action"] = "HOLD"
            
            # Log decision
            self.log_decision(
                decision_type="TRADE_SIGNAL",
                reasoning=signal.get("reasoning", ""),
                input_data=symbol_data,
                output_data=signal
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Strategy analysis error: {e}")
            return {
                "action": "HOLD",
                "symbol": symbol_data.get("symbol"),
                "confidence": 0,
                "error": str(e)
            }
    
    def _build_prompt(self, symbol_data: Dict[str, Any]) -> str:
        """Build analysis prompt."""
        return f"""You are a 15-year swing trader specializing in Nifty 500 stocks.

SYMBOL DATA:
{json.dumps(symbol_data, indent=2)}

TRADING RULES:
- Stop Loss: 2% max below entry
- Target: 4-6% above entry (R:R > 2:1)
- Position Size: ₹50k max risk per trade
- Sector Exposure: < 20% portfolio
- Confidence: > 75% only

SWING SETUPS (require 2+ confirmations):
1. Oversold Reversal: RSI < 35 + MACD bullish cross + volume > 1.5x avg
2. Breakout: Close > BB Upper + ADX > 25 + volume surge
3. Pullback: Close > VWAP + hammer candle + support bounce
4. Trend Continuation: EMA20 > EMA50 + pullback to EMA20

OUTPUT FORMAT (JSON only):
{{
    "action": "BUY|SELL|HOLD",
    "symbol": "NSE|TCS-EQ",
    "entry_price": 3245.5,
    "sl_price": 3180.6,
    "target_price": 3377.2,
    "confidence": 82,
    "reasoning": "RSI 28 + MACD cross + VWAP bounce",
    "risk_reward": 2.1,
    "position_size": 77
}}

Analyze and return JSON:"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to structured signal."""
        try:
            # Extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            signal = json.loads(response.strip())
            return signal
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {"action": "HOLD", "error": "Invalid JSON"}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process analysis request."""
        return self.analyze(input_data)
```

---

## Agent #4: Telegram Assistant

### Implementation

```python
# agents/telegram_assistant.py
from agents.base_agent import BaseAgent
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from database.repositories.order_repo import OrderRepository
from database.repositories.trade_repo import TradeRepository
from services.trading_service import TradingService
from typing import Dict, Any

class TelegramAssistant(BaseAgent):
    """Telegram bot interface."""
    
    def __init__(self, bot_token: str):
        super().__init__("telegram_assistant", "chatbot")
        self.bot_token = bot_token
        self.app = Application.builder().token(bot_token).build()
        self.order_repo = OrderRepository(get_session())
        self.trade_repo = TradeRepository(get_session())
        self.trading_service = TradingService(
            self.order_repo, self.trade_repo, None
        )
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers."""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("signals", self.signals_command))
        self.app.add_handler(CommandHandler("kill", self.kill_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context):
        """Handle /start command."""
        message = """🤖 Trading Bot Ready!

Commands:
/start - Show this message
/status - Show open positions
/signals - Show latest signals
/kill - Emergency: Close all positions

The bot will send trade signals for your approval."""
        await update.message.reply_text(message)
    
    async def status_command(self, update: Update, context):
        """Handle /status command."""
        # Get open positions
        trades = self.trade_repo.get_open_trades()
        
        if not trades:
            await update.message.reply_text("No open positions.")
            return
        
        message = "📊 Open Positions:\n\n"
        total_pnl = 0
        
        for trade in trades:
            pnl = trade.unrealized_pnl or 0
            total_pnl += pnl
            message += f"{trade.stock.symbol}: {trade.quantity} @ ₹{trade.entry_price}\n"
            message += f"  P&L: ₹{pnl:.2f} ({trade.pnl_percent:.2f}%)\n\n"
        
        message += f"Total P&L: ₹{total_pnl:.2f}"
        await update.message.reply_text(message)
    
    async def send_signal(self, signal: Dict[str, Any], chat_id: int):
        """Send trade signal for approval."""
        message = f"""🤖 New Trade Signal:

Symbol: {signal['symbol']}
Action: {signal['action']}
Entry: ₹{signal['entry_price']}
SL: ₹{signal['sl_price']}
Target: ₹{signal['target_price']}
Confidence: {signal['confidence']}%

Reasoning: {signal['reasoning']}"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{signal['symbol']}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{signal['symbol']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.app.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context):
        """Handle inline button presses."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("approve_"):
            symbol = data.replace("approve_", "")
            await self._approve_signal(symbol, query.message.chat_id)
        elif data.startswith("reject_"):
            symbol = data.replace("reject_", "")
            await query.edit_message_text(f"❌ Signal rejected: {symbol}")
    
    async def _approve_signal(self, symbol: str, chat_id: int):
        """Approve and execute signal."""
        # Get signal from database
        signal = self.order_repo.get_pending_signal(symbol)
        if not signal:
            await self.app.bot.send_message(chat_id, "Signal not found.")
            return
        
        # Execute order
        order = self.trading_service.place_order(signal)
        
        if order:
            message = f"""✅ Order Placed:

Symbol: {symbol}
Quantity: {order.quantity}
Entry: ₹{order.entry_price}
Order ID: {order.broker_order_id}"""
            await self.app.bot.send_message(chat_id, message)
        else:
            await self.app.bot.send_message(chat_id, "❌ Order failed.")
    
    async def start_polling(self):
        """Start bot polling."""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Telegram message."""
        # This is handled by handlers
        return {}
```

---

## Agent #5: News Sentiment Analyst

### Implementation

```python
# agents/news_sentiment_analyst.py
from agents.base_agent import BaseAgent
from database.repositories.analysis_repo import AnalysisRepository
from database.session import get_session
from data_sources.news_fetcher import NewsFetcher
from typing import Dict, Any, List
import json
from datetime import datetime, date
from loguru import logger

class NewsSentimentAnalyst(BaseAgent):
    """News aggregation and sentiment analysis agent."""
    
    def __init__(self):
        super().__init__("news_sentiment_analyst", "strategy")
        self.news_fetcher = NewsFetcher()
        self.repo = AnalysisRepository(get_session())
        self.fetch_interval = 15  # minutes
    
    def fetch_news(self) -> List[Dict[str, Any]]:
        """Fetch news from all configured sources."""
        try:
            articles = []
            sources = self.news_fetcher.get_active_sources()
            
            for source in sources:
                source_articles = self.news_fetcher.fetch_from_source(source)
                articles.extend(source_articles)
            
            # Deduplicate by URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            logger.info(f"Fetched {len(unique_articles)} unique articles")
            return unique_articles
            
        except Exception as e:
            logger.error(f"News fetching error: {e}")
            return []
    
    def categorize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize article using LLM."""
        prompt = f"""Analyze this news article and determine:

1. Category: 'stock_specific', 'sector', 'macro', 'government', or 'international'
2. If macro: What specific macro event? (rbi_rate_cut, gdp_growth, etc.)
3. Which sectors are affected? (if applicable)
4. Which stocks are mentioned? (if stock-specific)

ARTICLE:
Title: {article['title']}
Content: {article['content'][:1000]}  # First 1000 chars

OUTPUT (JSON only):
{{
    "category": "macro",
    "is_macro": true,
    "macro_category": "rbi_rate_cut",
    "affected_sectors": ["BANKING", "REAL_ESTATE"],
    "mentioned_stocks": []
}}"""
        
        try:
            response = self.llm.invoke(prompt)
            # Parse JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            categorization = json.loads(response.strip())
            return categorization
        except Exception as e:
            logger.error(f"Categorization error: {e}")
            return {"category": "unknown", "is_macro": False}
    
    def analyze_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze article sentiment using DeepSeek R1 7B."""
        prompt = f"""You are a financial sentiment analyst specializing in Indian stock markets.

Analyze the following news article and extract sentiment information.

ARTICLE:
Title: {article['title']}
Content: {article['content']}
Category: {article.get('category', 'unknown')}
Published: {article.get('published_date', 'unknown')}

TASK:
1. Determine overall sentiment: -1.0 (very bearish) to +1.0 (very bullish)
2. Assess confidence: 0.0 (uncertain) to 1.0 (very confident)
3. Identify key factors affecting sentiment
4. Determine if this is stock-specific, sector-wide, or macro-level

OUTPUT FORMAT (JSON only):
{{
    "overall_sentiment": 0.65,
    "confidence": 0.82,
    "sentiment_breakdown": {{
        "stock_specific": 0.70,
        "sector": 0.60,
        "macro": 0.55
    }},
    "key_factors": [
        "TCS wins $500M deal",
        "IT sector outlook positive"
    ],
    "reasoning": "Article mentions TCS deal win and positive IT sector outlook. Overall bullish sentiment with high confidence."
}}

IMPORTANT:
- For macro/government news, consider broader market impact
- Negative news can sometimes be bullish (e.g., rate cuts)
- Consider Indian market context and regulations
- Be conservative with confidence scores"""
        
        try:
            response = self.llm.invoke(prompt)
            # Parse JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            sentiment = json.loads(response.strip())
            return sentiment
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "overall_sentiment": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def propagate_macro_sentiment(
        self, 
        macro_article: Dict[str, Any],
        macro_sentiment: float
    ) -> List[Dict[str, Any]]:
        """Propagate macro sentiment to individual stocks."""
        from config.constants import MACRO_SECTOR_IMPACT
        
        macro_category = macro_article.get('macro_category')
        if not macro_category:
            return []
        
        # Get sector impact
        sector_impacts = MACRO_SECTOR_IMPACT.get(macro_category, {})
        
        # Get all stocks and their sectors
        stocks = self.repo.get_all_stocks_with_sectors()
        
        propagated_sentiments = []
        for stock in stocks:
            sector = stock.get('sector')
            if not sector or sector not in sector_impacts:
                continue
            
            sector_impact = sector_impacts[sector]
            
            # Calculate stock-specific sentiment
            stock_sentiment = macro_sentiment * sector_impact
            
            # Apply stock-specific multiplier (beta, market cap)
            stock_multiplier = self._get_stock_sensitivity(stock)
            final_sentiment = stock_sentiment * stock_multiplier
            
            propagated_sentiments.append({
                'stock_id': stock['id'],
                'news_article_id': macro_article['id'],
                'macro_sentiment': macro_sentiment,
                'sector_impact': sector_impact,
                'stock_sentiment': final_sentiment
            })
        
        return propagated_sentiments
    
    def _get_stock_sensitivity(self, stock: Dict[str, Any]) -> float:
        """Calculate stock sensitivity to macro events."""
        beta = stock.get('beta', 1.0)
        market_cap = stock.get('market_cap', 0)
        
        # Beta multiplier (high beta = more sensitive)
        beta_multiplier = min(beta / 1.0, 1.5)  # Cap at 1.5x
        
        # Market cap dampener (large cap = less sensitive)
        if market_cap > 100000:  # > ₹1L cr
            cap_multiplier = 0.8
        elif market_cap > 50000:  # > ₹50K cr
            cap_multiplier = 0.9
        else:
            cap_multiplier = 1.0
        
        return beta_multiplier * cap_multiplier
    
    def aggregate_daily_sentiment(self, stock_id: int, date: date) -> Dict[str, Any]:
        """Aggregate daily sentiment from all sources."""
        # Get stock-specific sentiment
        stock_articles = self.repo.get_articles_for_stock(stock_id, date)
        stock_sentiment = self._calculate_aggregate_sentiment(stock_articles)
        
        # Get sector sentiment
        sector = self.repo.get_stock_sector(stock_id)
        sector_articles = self.repo.get_sector_articles(sector, date)
        sector_sentiment = self._calculate_aggregate_sentiment(sector_articles)
        
        # Get macro sentiment (propagated)
        macro_sentiment = self.repo.get_macro_sentiment_for_stock(stock_id, date)
        
        # Weighted aggregation
        overall_sentiment = (
            stock_sentiment * 0.5 +      # 50% weight
            sector_sentiment * 0.3 +     # 30% weight
            macro_sentiment * 0.2        # 20% weight
        )
        
        return {
            'stock_id': stock_id,
            'date': date,
            'overall_sentiment': overall_sentiment,
            'stock_specific_sentiment': stock_sentiment,
            'sector_sentiment': sector_sentiment,
            'macro_sentiment': macro_sentiment,
            'confidence': self._calculate_confidence(stock_articles, sector_articles)
        }
    
    def _calculate_aggregate_sentiment(self, articles: List[Dict]) -> float:
        """Calculate aggregate sentiment from articles."""
        if not articles:
            return 0.0
        
        sentiments = [a.get('sentiment', 0.0) for a in articles if a.get('sentiment')]
        if not sentiments:
            return 0.0
        
        # Weighted average by confidence
        total_weight = sum(a.get('confidence', 0.5) for a in articles)
        weighted_sum = sum(s * a.get('confidence', 0.5) for s, a in zip(sentiments, articles))
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_confidence(self, stock_articles: List, sector_articles: List) -> float:
        """Calculate overall confidence based on article count and quality."""
        total_articles = len(stock_articles) + len(sector_articles)
        
        # More articles = higher confidence (capped at 0.9)
        article_confidence = min(0.9, 0.3 + (total_articles * 0.1))
        
        # Average confidence from articles
        avg_confidence = 0.0
        all_articles = stock_articles + sector_articles
        if all_articles:
            confidences = [a.get('confidence', 0.5) for a in all_articles]
            avg_confidence = sum(confidences) / len(confidences)
        
        # Combined confidence
        return (article_confidence * 0.4 + avg_confidence * 0.6)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process news fetching and sentiment analysis."""
        try:
            # Fetch news
            articles = self.fetch_news()
            
            # Process each article
            for article in articles:
                # Categorize
                categorization = self.categorize_article(article)
                article.update(categorization)
                
                # Analyze sentiment
                sentiment = self.analyze_sentiment(article)
                article['sentiment'] = sentiment.get('overall_sentiment', 0.0)
                article['sentiment_confidence'] = sentiment.get('confidence', 0.0)
                
                # Store article
                stored_article = self.repo.store_article(article)
                
                # If macro, propagate to stocks
                if article.get('is_macro'):
                    propagated = self.propagate_macro_sentiment(
                        stored_article,
                        sentiment.get('overall_sentiment', 0.0)
                    )
                    self.repo.store_macro_sentiment_mappings(propagated)
            
            # Aggregate daily sentiment for all stocks
            today = date.today()
            stocks = self.repo.get_all_stocks()
            for stock in stocks:
                daily_sentiment = self.aggregate_daily_sentiment(stock['id'], today)
                self.repo.store_daily_sentiment(daily_sentiment)
            
            return {
                'status': 'success',
                'articles_processed': len(articles),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"News sentiment processing error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
```

---

## Agent #6: Portfolio Guardian

### Implementation

```python
# agents/portfolio_guardian.py
from agents.base_agent import BaseAgent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.repositories.trade_repo import TradeRepository
from data_sources.shoonya_scraper import ShoonyaScraper
from typing import Dict, Any
import asyncio

class PortfolioGuardian(BaseAgent):
    """Portfolio monitoring and risk management."""
    
    def __init__(self):
        super().__init__("portfolio_guardian", "strategy")
        self.scheduler = AsyncIOScheduler()
        self.trade_repo = TradeRepository(get_session())
        self.shoonya = ShoonyaScraper()
        self.interval = 300  # 5 minutes
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        self.scheduler.add_job(
            self.check_positions,
            'interval',
            seconds=self.interval,
            id='position_check'
        )
        self.scheduler.start()
    
    async def check_positions(self):
        """Check all open positions."""
        trades = self.trade_repo.get_open_trades()
        
        for trade in trades:
            # Get current price
            current_price = await self.shoonya.get_live_price(trade.stock.symbol)
            
            # Check SL breach
            if current_price < trade.stop_loss:
                await self._execute_stop_loss(trade, current_price)
                continue
            
            # Check near target
            if current_price > trade.target * 0.95:
                await self._alert_near_target(trade, current_price)
            
            # Check trailing stop
            if trade.pnl_percent > 8:
                await self._update_trailing_stop(trade, current_price)
            
            # Update unrealized P&L
            self._update_pnl(trade, current_price)
    
    async def _execute_stop_loss(self, trade, current_price):
        """Execute stop loss."""
        logger.warning(f"SL breach: {trade.stock.symbol} @ {current_price}")
        
        # Place sell order
        order = self.trading_service.place_sell_order(
            trade.stock.symbol,
            trade.quantity,
            current_price
        )
        
        # Update trade
        trade.exit_price = current_price
        trade.status = "STOP_LOSS_HIT"
        trade.closed_at = datetime.now()
        self.trade_repo.update_trade(trade)
        
        # Send alert
        await self._send_alert(
            f"🚨 SL Hit: {trade.stock.symbol} @ ₹{current_price}"
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring request."""
        return {"status": "monitoring"}
```

---

## Common Patterns

### Error Handling Pattern

```python
def safe_process(self, input_data):
    """Safe processing with error handling."""
    try:
        result = self.process(input_data)
        return result
    except Exception as e:
        logger.error(f"{self.name} error: {e}")
        return {"error": str(e), "status": "failed"}
```

### Logging Pattern

```python
def log_decision(self, decision_type, reasoning, input_data, output_data):
    """Log all agent decisions."""
    self.log_decision(
        agent_name=self.name,
        decision_type=decision_type,
        reasoning=reasoning,
        input_data=input_data,
        output_data=output_data
    )
```

---

## Testing

### Unit Tests

```python
# tests/test_librarian.py
def test_librarian_translation():
    librarian = DatabaseLibrarian()
    sql = librarian.translate("oversold RSI stocks")
    assert "rsi" in sql.lower()
    assert "select" in sql.lower()
```

### Integration Tests

```python
# tests/test_integration.py
def test_signal_generation_flow():
    librarian = DatabaseLibrarian()
    scraper = DataScraper()
    strategy = StrategySpecialist()
    
    # Get candidates
    candidates = librarian.process({"query": "oversold RSI"})
    
    # Fetch data
    data = scraper.process({"symbol": candidates[0]["symbol"]})
    
    # Generate signal
    signal = strategy.process(data)
    
    assert signal["confidence"] > 0
```

---

**Next Documents**:
- `04_CONFIGURATION_REFERENCE.md` - Complete configuration guide
- `05_DEPLOYMENT_AND_OPERATIONS.md` - Deployment guide
