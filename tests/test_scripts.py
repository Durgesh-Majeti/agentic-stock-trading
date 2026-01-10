"""Unit tests for scripts."""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock


def test_backup_database_script():
    """Test database backup script."""
    from scripts.backup_database import backup_database
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy database
        db_path = Path(tmpdir) / "test.db"
        db_path.write_text("dummy database content")
        
        # Mock settings
        with patch('scripts.backup_database.settings') as mock_settings:
            mock_settings.database_url = f"sqlite:///{db_path}"
            
            backup_path = backup_database(backup_dir=Path(tmpdir) / "backups")
            
            assert backup_path.exists()
            assert backup_path.name.startswith("trading_")


def test_validate_environment_script():
    """Test environment validation script."""
    from scripts.validate_environment import (
        validate_ollama_config,
        validate_database_config,
        validate_paths,
    )
    
    # Test with valid config
    with patch('scripts.validate_environment.settings') as mock_settings:
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_strategy_model = "test-model"
        mock_settings.ollama_database_model = "test-model"
        mock_settings.ollama_chatbot_model = "test-model"
        
        assert validate_ollama_config() is True


def test_test_configuration_script():
    """Test configuration test script."""
    from scripts.test_configuration import test_settings_loading, test_model_config
    
    assert test_settings_loading() is True
    assert test_model_config() is True
