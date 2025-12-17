"""Database configuration for SQLite"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# SQLite database path (will be mounted as volume in Docker)
DB_PATH = Path("/app/data/users.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    pool_pre_ping=True
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