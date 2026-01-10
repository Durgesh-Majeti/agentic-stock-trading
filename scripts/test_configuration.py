"""Configuration test script."""
import sys
from pathlib import Path
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.ollama_config import OllamaModelConfig, ModelRole
from services.ollama_service import OllamaService


def test_settings_loading():
    """Test that settings load correctly."""
    logger.info("Testing settings loading...")
    
    try:
        # Test basic settings
        assert settings.database_url, "Database URL not set"
        assert settings.ollama_base_url, "Ollama base URL not set"
        
        logger.info("✅ Settings loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Settings loading failed: {e}")
        return False


def test_model_config():
    """Test model configuration."""
    logger.info("Testing model configuration...")
    
    try:
        # Test model retrieval for each role
        for role in ModelRole:
            model = OllamaModelConfig.get_model_for_role(role)
            fallback = OllamaModelConfig.get_model_for_role(role, use_fallback=True)
            
            assert model, f"No model configured for {role.value}"
            assert fallback, f"No fallback model configured for {role.value}"
            
            logger.info(f"  {role.value}: {model} (fallback: {fallback})")
        
        logger.info("✅ Model configuration valid")
        return True
    except Exception as e:
        logger.error(f"❌ Model configuration test failed: {e}")
        return False


def test_ollama_service():
    """Test Ollama service initialization."""
    logger.info("Testing Ollama service...")
    
    try:
        service = OllamaService()
        
        if not service.is_available:
            logger.warning("⚠️ Ollama service not available (server may not be running)")
            return False
        
        # Test model listing
        models = service.list_available_models()
        logger.info(f"  Found {len(models)} available models")
        
        logger.info("✅ Ollama service test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Ollama service test failed: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    logger.info("Testing database connection...")
    
    try:
        from database.session import get_db
        
        with get_db() as db:
            # Simple query to test connection
            from sqlalchemy import text
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        logger.info("✅ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Starting configuration tests...")
    
    tests = [
        ("Settings Loading", test_settings_loading),
        ("Model Configuration", test_model_config),
        ("Ollama Service", test_ollama_service),
        ("Database Connection", test_database_connection),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("Test Summary:")
    logger.info("="*50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ All configuration tests passed")
        return 0
    else:
        logger.warning("\n⚠️ Some configuration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
