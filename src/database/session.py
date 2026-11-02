import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base
from .backup import rotate_backups
from dotenv import load_dotenv

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure environment variables are loaded from the root .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Determine environment (default to production for safety)
APP_ENV = os.environ.get("APP_ENV", "production")
DATABASE_PATH_ENV = os.environ.get("DATABASE_PATH")

if DATABASE_PATH_ENV:
    DATABASE_PATH = DATABASE_PATH_ENV
else:
    if APP_ENV == "development":
        DATABASE_FILE = "gtd_dev.db"
    elif APP_ENV == "test":
        DATABASE_FILE = "test_gtd.db"
    else:
        DATABASE_FILE = "gtd.db"
    DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_FILE)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Print warning for production
if APP_ENV == "production":
    # In a real app, we might want to log this or handle it more formally
    pass

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_schema_migrations(target_engine=None):
    """
    Safely creates any missing tables and adds new columns to existing SQLite tables
    without modifying or losing existing data.
    """
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)

    migrations = {
        "h2_role": [
            ("todoist_project_id", "VARCHAR"),
            ("todoist_project_name", "VARCHAR"),
        ],
        "ambition": [
            ("todoist_label_id", "VARCHAR"),
            ("todoist_label_name", "VARCHAR"),
        ],
        "task": [
            ("todoist_task_id", "VARCHAR"),
            ("todoist_due_date", "VARCHAR"),
            ("todoist_priority", "INTEGER DEFAULT 1"),
            ("todoist_created_at", "DATETIME"),
        ],
        "inbox": [
            ("todoist_task_id", "VARCHAR"),
            ("todoist_due_date", "VARCHAR"),
            ("todoist_priority", "INTEGER DEFAULT 1"),
            ("todoist_created_at", "DATETIME"),
        ],
    }

    with eng.begin() as conn:
        for table_name, columns in migrations.items():
            res = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            existing_cols = {row[1] for row in res}
            for col_name, col_type in columns:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))

def init_db():
    """
    Initialize the database and apply non-destructive schema migrations.
    """
    if APP_ENV == "production" and os.path.exists(DATABASE_PATH):
        rotate_backups(DATABASE_PATH)

    ensure_schema_migrations(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
