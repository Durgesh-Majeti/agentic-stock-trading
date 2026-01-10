"""Test local Ollama connection and list available models."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.ollama_service import OllamaService
from loguru import logger


def main():
    """Test local Ollama connection."""
    logger.info("Testing local Ollama server connection...")
    logger.info("💡 Make sure Ollama is running: 'ollama serve'")
    
    service = OllamaService()
    
    if not service.is_available:
        logger.error("❌ Local Ollama server is not available")
        logger.error("💡 Start Ollama server with: ollama serve")
        return 1
    
    logger.info("✅ Local Ollama server connection successful!")
    
    # List available models
    logger.info("\nFetching available models...")
    models = service.list_available_models()
    
    if models:
        logger.info(f"\nFound {len(models)} available models:")
        for i, model in enumerate(models[:20], 1):  # Show first 20
            model_id = model.get('id', 'N/A')
            logger.info(f"  {i}. {model_id}")
        if len(models) > 20:
            logger.info(f"  ... and {len(models) - 20} more")
    else:
        logger.warning("No models found")
        logger.info("💡 Pull models with: ollama pull <model_name>")
    
    # Test configured models
    logger.info("\nTesting configured models...")
    from config.ollama_config import ModelRole, OllamaModelConfig
    
    for role in [ModelRole.STRATEGY, ModelRole.DATABASE, ModelRole.CHATBOT, ModelRole.NEWS_SENTIMENT, ModelRole.GUARDIAN]:
        model_name = OllamaModelConfig.get_model_for_role(role)
        logger.info(f"\nTesting {role.value} model: {model_name}")
        is_available = service.test_model(model_name)
        if is_available:
            logger.info(f"  ✅ {model_name} is available")
        else:
            logger.warning(f"  ⚠️ {model_name} is not available")
            logger.info(f"  💡 Pull model with: ollama pull {model_name}")
            # Try fallback
            fallback = OllamaModelConfig.get_model_for_role(role, use_fallback=True)
            logger.info(f"  Trying fallback: {fallback}")
            if service.test_model(fallback):
                logger.info(f"  ✅ Fallback {fallback} is available")
            else:
                logger.error(f"  ❌ Fallback {fallback} is not available")
                logger.info(f"  💡 Pull fallback with: ollama pull {fallback}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
