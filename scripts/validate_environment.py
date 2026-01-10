"""Environment validation script."""
import sys
from pathlib import Path
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from utils.validators import validate_api_key, validate_email
import os


def validate_ollama_config():
    """Validate Ollama configuration."""
    logger.info("Validating Ollama configuration...")
    issues = []
    
    if not settings.ollama_base_url:
        issues.append("OLLAMA_BASE_URL is not set")
    elif not settings.ollama_base_url.startswith("http"):
        issues.append(f"Invalid OLLAMA_BASE_URL format: {settings.ollama_base_url}")
    
    if not settings.ollama_strategy_model:
        issues.append("OLLAMA_STRATEGY_MODEL is not set")
    
    if not settings.ollama_database_model:
        issues.append("OLLAMA_DATABASE_MODEL is not set")
    
    if not settings.ollama_chatbot_model:
        issues.append("OLLAMA_CHATBOT_MODEL is not set")
    
    if issues:
        logger.error(f"❌ Ollama config issues: {issues}")
        return False
    
    logger.info("✅ Ollama configuration valid")
    return True


def validate_telegram_config():
    """Validate Telegram configuration."""
    logger.info("Validating Telegram configuration...")
    issues = []
    
    if not settings.telegram_bot_token:
        issues.append("TELEGRAM_BOT_TOKEN is not set")
    elif not validate_api_key(settings.telegram_bot_token, min_length=20):
        issues.append("TELEGRAM_BOT_TOKEN format is invalid")
    
    if issues:
        logger.warning(f"⚠️ Telegram config issues: {issues}")
        return False
    
    logger.info("✅ Telegram configuration valid")
    return True


def validate_shoonya_config():
    """Validate Shoonya configuration."""
    logger.info("Validating Shoonya configuration...")
    issues = []
    
    required_fields = [
        ("SHOONYA_USER_ID", settings.shoonya_user_id),
        ("SHOONYA_PASSWORD", settings.shoonya_password),
        ("SHOONYA_TWO_FA", settings.shoonya_two_fa),
        ("SHOONYA_VENDOR_CODE", settings.shoonya_vendor_code),
    ]
    
    for field_name, field_value in required_fields:
        if not field_value:
            issues.append(f"{field_name} is not set")
    
    if issues:
        logger.warning(f"⚠️ Shoonya config issues: {issues}")
        return False
    
    logger.info("✅ Shoonya configuration valid")
    return True


def validate_database_config():
    """Validate database configuration."""
    logger.info("Validating database configuration...")
    
    if not settings.database_url:
        logger.error("❌ DATABASE_URL is not set")
        return False
    
    if not settings.database_url.startswith("sqlite:///"):
        logger.warning(f"⚠️ Non-SQLite database URL: {settings.database_url}")
    
    # Check if database directory exists
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    db_dir = db_path.parent
    if not db_dir.exists():
        logger.warning(f"⚠️ Database directory does not exist: {db_dir}")
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created database directory: {db_dir}")
    
    logger.info("✅ Database configuration valid")
    return True


def validate_paths():
    """Validate required paths exist."""
    logger.info("Validating required paths...")
    
    required_dirs = [
        project_root / "data",
        project_root / "logs",
        project_root / "backups",
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            logger.warning(f"⚠️ Directory does not exist: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {dir_path}")
    
    logger.info("✅ Required paths validated")
    return True


def validate_python_version():
    """Validate Python version."""
    logger.info("Validating Python version...")
    
    import sys
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        logger.error(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    
    logger.info(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def main():
    """Main validation function."""
    logger.info("Starting environment validation...")
    
    checks = [
        ("Python Version", validate_python_version),
        ("Paths", validate_paths),
        ("Database Config", validate_database_config),
        ("Ollama Config", validate_ollama_config),
        ("Telegram Config", validate_telegram_config),
        ("Shoonya Config", validate_shoonya_config),
    ]
    
    results = {}
    for check_name, check_func in checks:
        logger.info(f"\n--- {check_name} ---")
        try:
            results[check_name] = check_func()
        except Exception as e:
            logger.error(f"❌ {check_name} check failed: {e}")
            results[check_name] = False
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("Validation Summary:")
    logger.info("="*50)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ All environment checks passed")
        return 0
    else:
        logger.warning("\n⚠️ Some environment checks failed or have warnings")
        return 1


if __name__ == "__main__":
    sys.exit(main())
