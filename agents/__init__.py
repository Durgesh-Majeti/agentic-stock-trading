"""
Agents Module

All agents inherit from BaseAgent and implement the process() method.
Agents are designed to work with the orchestrator.
"""

from agents.base_agent import BaseAgent
from agents.database_librarian import DatabaseLibrarian
from agents.data_scraper import DataScraper
from agents.strategy_specialist import StrategySpecialist
from agents.news_sentiment_analyst import NewsSentimentAnalyst

__all__ = [
    "BaseAgent",
    "DatabaseLibrarian",
    "DataScraper",
    "StrategySpecialist",
    "NewsSentimentAnalyst",
]

__version__ = "1.2.0"
