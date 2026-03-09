
import os
import shutil
from datetime import datetime
from src.database.session import BASE_DIR, DATABASE_PATH, engine
from src.database.models import Base

def backup_production():
    """Create a backup of the production database."""
    if os.path.exists(DATABASE_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DATABASE_PATH}.{timestamp}.bak"
        print(f"Backing up production database to {backup_path}...")
        shutil.copy2(DATABASE_PATH, backup_path)
        return backup_path
    return None

def run_migration():
    """Apply schema changes to the production database."""
    print("Starting migration to production...")
    
    # Ensure we are targeting the production file
    if not DATABASE_PATH.endswith("gtd.db"):
        print(f"Error: DATABASE_PATH ({DATABASE_PATH}) does not look like a production path.")
        return

    # 1. Backup
    backup_production()

    # 2. Apply Schema Changes
    # SQLAlchemy's create_all will only create missing tables
    print("Applying schema changes (creating missing tables)...")
    Base.metadata.create_all(bind=engine)
    
    print("Migration successful.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        run_migration()
    else:
        print("This script will apply changes to the PRODUCTION database.")
        print("Usage: python scripts/migrate.py --confirm")
