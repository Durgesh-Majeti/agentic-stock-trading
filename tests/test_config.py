"""Unit tests for configuration."""
import pytest
from config.settings import settings
from config.ollama_config import OllamaModelConfig, ModelRole
from config.constants import OrderStatus, OrderType, TradeStatus


def test_settings_loaded():
    """Test that settings are loaded."""
    assert settings.database_url is not None
    assert settings.ollama_base_url is not None


def test_model_config():
    """Test model configuration."""
    for role in ModelRole:
        model = OllamaModelConfig.get_model_for_role(role)
        assert model is not None
        assert isinstance(model, str)


def test_constants():
    """Test constants."""
    assert OrderStatus.PENDING_APPROVAL == "PENDING_APPROVAL"
    assert OrderType.BUY == "BUY"
    assert TradeStatus.OPEN == "OPEN"
