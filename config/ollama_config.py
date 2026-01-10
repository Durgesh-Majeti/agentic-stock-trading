"""Ollama model configuration for different agent roles."""
from enum import Enum
from config.settings import settings


class ModelRole(str, Enum):
    """Model roles for different agent types."""
    STRATEGY = "strategy"      # Trading decisions (thinking mode)
    DATABASE = "database"      # SQL generation and optimization
    CHATBOT = "chatbot"        # User interaction (agentic, tool use)
    NEWS_SENTIMENT = "news_sentiment"  # News sentiment analysis
    GUARDIAN = "guardian"      # Portfolio monitoring


class OllamaModelConfig:
    """Configuration for local Ollama models per agent role."""
    
    @staticmethod
    def get_model_for_role(role: ModelRole, use_fallback: bool = False) -> str:
        """Get model name for a specific role.
        
        Args:
            role: The agent role (STRATEGY, DATABASE, CHATBOT, or GUARDIAN)
            use_fallback: Whether to use fallback model
            
        Returns:
            Model name string
        """
        model_map = {
            ModelRole.STRATEGY: {
                "primary": settings.ollama_strategy_model,
                "fallback": settings.ollama_strategy_fallback,
            },
            ModelRole.DATABASE: {
                "primary": settings.ollama_database_model,
                "fallback": settings.ollama_database_fallback,
            },
            ModelRole.CHATBOT: {
                "primary": settings.ollama_chatbot_model,
                "fallback": settings.ollama_chatbot_fallback,
            },
            ModelRole.NEWS_SENTIMENT: {
                "primary": settings.ollama_news_sentiment_model,
                "fallback": settings.ollama_news_sentiment_fallback,
            },
            ModelRole.GUARDIAN: {
                "primary": settings.ollama_guardian_model,
                "fallback": settings.ollama_strategy_fallback,  # Use strategy fallback
            },
        }
        
        models = model_map[role]
        return models["fallback"] if use_fallback else models["primary"]
    
    @staticmethod
    def get_model_features(role: ModelRole) -> dict:
        """Get features for a specific model role.
        
        Args:
            role: The agent role
            
        Returns:
            Dictionary of model features
        """
        features_map = {
            ModelRole.STRATEGY: {
                "thinking_mode": True,
                "context_window": "128k",
                "use_case": "complex_reasoning",
                "financial_modeling": True,
            },
            ModelRole.DATABASE: {
                "sql_generation": True,
                "code_optimization": True,
                "query_translation": True,
            },
            ModelRole.CHATBOT: {
                "agentic": True,
                "tool_use": True,
                "database_connectivity": True,
                "real_time_queries": True,
            },
            ModelRole.NEWS_SENTIMENT: {
                "sentiment_analysis": True,
                "complex_reasoning": True,
                "structured_output": True,
                "macro_categorization": True,
            },
            ModelRole.GUARDIAN: {
                "monitoring": True,
                "risk_analysis": True,
                "decision_making": True,
            },
        }
        return features_map.get(role, {})
    
    @staticmethod
    def get_base_url() -> str:
        """Get local Ollama base URL."""
        return settings.ollama_base_url