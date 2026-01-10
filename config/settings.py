"""Application settings using Pydantic."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env (for backward compatibility)
    )
    
    # Ollama Local Configuration
    ollama_base_url: str = "http://localhost:11434"  # Local Ollama server
    
    # Model Selection (local Ollama models - must be pulled locally)
    ollama_strategy_model: str = "deepseek-r1:7b"  # Strategy specialist model
    ollama_strategy_fallback: str = "qwen2.5:7b"  # Fallback for strategy
    ollama_database_model: str = "qwen2.5-coder:7b-instruct"  # Database librarian model
    ollama_database_fallback: str = "codegemma:7b"  # Fallback for database
    ollama_chatbot_model: str = "gemma2:2b-instruct-q4_K_M"  # Telegram assistant model (quantized for speed)
    ollama_chatbot_fallback: str = "phi3:mini"  # Fallback for chatbot
    ollama_guardian_model: str = "deepseek-r1:7b"  # Portfolio guardian model
    
    # Telegram Bot
    telegram_bot_token: str = ""
    
    # Shoonya API
    shoonya_user_id: str = ""
    shoonya_password: str = ""
    shoonya_two_fa: str = ""
    shoonya_vendor_code: str = ""
    shoonya_api_secret: str = ""
    shoonya_imei: str = ""
    
    # Database
    database_url: str = "sqlite:///./data/trading.db"
    
    # Trading Settings
    max_position_size: float = 10000.0
    risk_percentage: float = 2.0
    enable_live_trading: bool = False
    portfolio_heat_threshold: float = 80.0  # Block trades if >80% exposure
    
    # Watchlist
    watchlist: str = "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK"
    
    # Data Collection
    data_update_interval: int = 300  # seconds
    sentiment_update_interval: int = 600  # seconds
    heartbeat_interval: int = 1800  # seconds
    
    # Resilience Layer
    stop_loss_check_interval: int = 300  # seconds
    portfolio_heat_check_interval: int = 300  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/trading_app.log"
    
    @property
    def watchlist_symbols(self) -> List[str]:
        """Get watchlist as list of uppercase symbols."""
        return [s.strip().upper() for s in self.watchlist.split(",") if s.strip()]
    
    @property
    def database_path(self) -> Path:
        """Get database file path."""
        db_url = self.database_url.replace("sqlite:///", "")
        return Path(db_url).parent


# Create necessary directories
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
