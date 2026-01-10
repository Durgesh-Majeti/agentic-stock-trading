"""News source configuration for sentiment analysis."""
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsSourceConfig:
    """Configuration for a news source."""
    name: str
    url: str
    type: str  # 'rss' or 'api'
    categories: List[str]
    fetch_frequency: int  # minutes
    is_active: bool = True
    api_key: str = ""
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }


# Free Indian News Sources
INDIAN_NEWS_SOURCES: List[NewsSourceConfig] = [
    NewsSourceConfig(
        name="economic_times_markets",
        url="https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        type="rss",
        categories=["markets", "stocks"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="economic_times_economy",
        url="https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
        type="rss",
        categories=["economy", "macro"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="economic_times_policy",
        url="https://economictimes.indiatimes.com/news/policy/rssfeeds/1052732854.cms",
        type="rss",
        categories=["policy", "government"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="moneycontrol_latest",
        url="https://www.moneycontrol.com/rss/latestnews.xml",
        type="rss",
        categories=["markets", "stocks", "general"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="moneycontrol_markets",
        url="https://www.moneycontrol.com/rss/marketreports.xml",
        type="rss",
        categories=["markets", "analysis"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="business_standard_markets",
        url="https://www.business-standard.com/rss/markets-106.rss",
        type="rss",
        categories=["markets", "stocks"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="business_standard_economy",
        url="https://www.business-standard.com/rss/economy-policy-108.rss",
        type="rss",
        categories=["economy", "macro", "policy"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="business_standard_companies",
        url="https://www.business-standard.com/rss/companies-101.rss",
        type="rss",
        categories=["companies", "stocks"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="livemint_markets",
        url="https://www.livemint.com/rss/markets",
        type="rss",
        categories=["markets", "stocks"],
        fetch_frequency=15
    ),
    NewsSourceConfig(
        name="financial_express_markets",
        url="https://www.financialexpress.com/feed/market/",
        type="rss",
        categories=["markets", "stocks"],
        fetch_frequency=15
    ),
]

# BSE Corporate Announcements (RSS Feed)
BSE_ANNOUNCEMENTS = NewsSourceConfig(
    name="bse_announcements",
    url="https://www.bseindia.com/rssxml/Corporate_Announcements.xml",
    type="rss",
    categories=["corporate", "announcements"],
    fetch_frequency=30,
    is_active=True,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml',
    }
)

# International Sources (Optional)
INTERNATIONAL_SOURCES: List[NewsSourceConfig] = [
    NewsSourceConfig(
        name="yahoo_finance",
        url="https://finance.yahoo.com/rss/",
        type="rss",
        categories=["international", "global"],
        fetch_frequency=30
    ),
]


def get_all_active_sources() -> List[NewsSourceConfig]:
    """Get all active news sources."""
    all_sources = INDIAN_NEWS_SOURCES + [BSE_ANNOUNCEMENTS] + INTERNATIONAL_SOURCES
    return [source for source in all_sources if source.is_active]


def get_source_by_name(name: str) -> NewsSourceConfig:
    """Get a specific news source by name."""
    all_sources = INDIAN_NEWS_SOURCES + [BSE_ANNOUNCEMENTS] + INTERNATIONAL_SOURCES
    for source in all_sources:
        if source.name == name:
            return source
    raise ValueError(f"News source '{name}' not found")


def get_sources_by_category(category: str) -> List[NewsSourceConfig]:
    """Get all sources that cover a specific category."""
    all_sources = INDIAN_NEWS_SOURCES + [BSE_ANNOUNCEMENTS] + INTERNATIONAL_SOURCES
    return [
        source for source in all_sources
        if source.is_active and category in source.categories
    ]
