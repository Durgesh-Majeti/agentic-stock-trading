"""Migration script to add sector and market_cap columns to stocks table."""
import sys
from pathlib import Path
import sqlite3

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import settings, fallback to default
try:
    from config.settings import settings
    db_url = settings.database_url.replace("sqlite:///", "")
except:
    db_url = "./data/trading.db"


def migrate_database():
    """Add sector and market_cap columns to stocks table if they don't exist."""
    # Get database path
    db_path = Path(db_url)
    
    if not db_path.exists():
        print(f"[ERROR] Database not found at {db_path}")
        return False
    
    print(f"Migrating database at {db_path}...")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(stocks)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add sector column if it doesn't exist
        if 'sector' not in columns:
            print("Adding 'sector' column to stocks table...")
            cursor.execute("ALTER TABLE stocks ADD COLUMN sector TEXT")
            print("[OK] Added 'sector' column")
        else:
            print("'sector' column already exists")
        
        # Add market_cap column if it doesn't exist
        if 'market_cap' not in columns:
            print("Adding 'market_cap' column to stocks table...")
            cursor.execute("ALTER TABLE stocks ADD COLUMN market_cap REAL")
            print("[OK] Added 'market_cap' column")
        else:
            print("'market_cap' column already exists")
        
        conn.commit()
        conn.close()
        
        print("[OK] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
