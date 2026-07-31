"""Database configuration for SQLite"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Default to the Docker volume while allowing local development, tests, and a
# future PostgreSQL migration to supply a standard DATABASE_URL.
DEFAULT_DB_PATH = Path("/app/data/users.db")
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_DB_PATH}",
)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    sqlite_path = Path(SQLALCHEMY_DATABASE_URL.removeprefix("sqlite:///"))
    if str(sqlite_path) != ":memory:":
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False, "timeout": 30}
else:
    connect_args = {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If tables already exist, that's fine - just log and continue
        # This can happen on container restarts
        import logging
        logger = logging.getLogger(__name__)
        if "already exists" in str(e).lower() or "table" in str(e).lower():
            logger.info("Database tables already exist, skipping creation")
        else:
            # Re-raise if it's a different error
            logger.error(f"Failed to initialize database: {e}")
            raise