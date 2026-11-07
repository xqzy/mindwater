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
            ("color", "VARCHAR DEFAULT '#0284c7'"),
            ("theme_key", "VARCHAR DEFAULT 'frozen'"),
        ],
        "ambition": [
            ("todoist_label_id", "VARCHAR"),
            ("todoist_label_name", "VARCHAR"),
            ("priority", "INTEGER DEFAULT 999"),
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

        # Normalize uninitialized ambition priorities sequentially (1..N)
        rows = conn.execute(
            text("SELECT id, priority FROM ambition WHERE status != 'archived' ORDER BY COALESCE(priority, 999) ASC, id ASC")
        ).fetchall()
        if any(r[1] is None or r[1] >= 999 for r in rows):
            for idx, r in enumerate(rows, start=1):
                conn.execute(text("UPDATE ambition SET priority = :p WHERE id = :id"), {"p": idx, "id": r[0]})

        # Assign distinct default cartoon/Disney themes & matching colors to existing roles if unset
        default_role_themes = [
            ("lion_king", "#d97706"),
            ("frozen", "#0284c7"),
            ("aladdin", "#7c3aed"),
            ("moana", "#0d9488"),
            ("toy_story", "#2563eb"),
            ("beauty_beast", "#e11d48"),
            ("little_mermaid", "#059669"),
            ("tangled", "#c026d3"),
            ("up", "#ea580c"),
            ("finding_nemo", "#f97316"),
            ("mulan", "#db2777"),
            ("wall_e", "#65a30d"),
            ("coco", "#ca8a04"),
            ("monsters_inc", "#0891b2"),
            ("peter_pan", "#16a34a"),
        ]
        role_rows = conn.execute(text("SELECT id, color, theme_key FROM h2_role ORDER BY id ASC")).fetchall()
        for idx, rr in enumerate(role_rows):
            r_id, r_color, r_theme = rr[0], rr[1], rr[2]
            if not r_theme or not r_color:
                t_key, t_color = default_role_themes[idx % len(default_role_themes)]
                conn.execute(
                    text("UPDATE h2_role SET theme_key = :tk, color = :c WHERE id = :id"),
                    {"tk": r_theme or t_key, "c": r_color or t_color, "id": r_id},
                )

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
