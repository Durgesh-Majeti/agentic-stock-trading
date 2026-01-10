"""Configuration package."""
from config.settings import settings
from config.ollama_config import OllamaModelConfig, ModelRole
from config.news_sources import (
    NewsSourceConfig,
    get_all_active_sources,
    get_source_by_name,
    get_sources_by_category,
    INDIAN_NEWS_SOURCES,
    NSE_ANNOUNCEMENTS,
    INTERNATIONAL_SOURCES
)

__all__ = [
    "settings",
    "OllamaModelConfig",
    "ModelRole",
    "NewsSourceConfig",
    "get_all_active_sources",
    "get_source_by_name",
    "get_sources_by_category",
    "INDIAN_NEWS_SOURCES",
    "NSE_ANNOUNCEMENTS",
    "INTERNATIONAL_SOURCES",
]
