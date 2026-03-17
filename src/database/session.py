import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .backup import rotate_backups
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def init_db():
    """
    Initialize the database. 
    In development/test, it's okay to create all.
    In production, this should be handled by migrations.
    """
    if APP_ENV == "production" and os.path.exists(DATABASE_PATH):
        rotate_backups(DATABASE_PATH)

    if APP_ENV != "production" or not os.path.exists(DATABASE_PATH):
        Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
