"""Database backup script."""
import sys
from pathlib import Path
from datetime import datetime
import shutil
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings


def backup_database(backup_dir: Path = None) -> Path:
    """Backup database to backup directory.
    
    Args:
        backup_dir: Backup directory (default: backups/ in project root)
        
    Returns:
        Path to backup file
    """
    # Get database path
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    # Create backup directory
    if backup_dir is None:
        backup_dir = project_root / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"trading_{timestamp}.db"
    backup_path = backup_dir / backup_filename
    
    # Copy database file
    logger.info(f"Backing up database to {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    # Verify backup
    if backup_path.exists() and backup_path.stat().st_size > 0:
        logger.info(f"✅ Backup successful: {backup_path} ({backup_path.stat().st_size} bytes)")
        return backup_path
    else:
        logger.error("❌ Backup failed: file not created or empty")
        raise RuntimeError("Backup failed")


def cleanup_old_backups(backup_dir: Path = None, keep_days: int = 30) -> int:
    """Remove backup files older than specified days.
    
    Args:
        backup_dir: Backup directory
        keep_days: Number of days to keep backups
        
    Returns:
        Number of files deleted
    """
    if backup_dir is None:
        backup_dir = project_root / "backups"
    
    if not backup_dir.exists():
        return 0
    
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    deleted_count = 0
    
    for backup_file in backup_dir.glob("trading_*.db"):
        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        if file_time < cutoff_date:
            logger.info(f"Deleting old backup: {backup_file}")
            backup_file.unlink()
            deleted_count += 1
    
    return deleted_count


def main():
    """Main backup function."""
    try:
        logger.info("Starting database backup...")
        backup_path = backup_database()
        logger.info(f"✅ Backup completed: {backup_path}")
        
        # Cleanup old backups
        deleted = cleanup_old_backups()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old backup(s)")
        
        return 0
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
