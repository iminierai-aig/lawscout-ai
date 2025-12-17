"""Authentication module initialization"""
from .routes import router
from .database import init_db

__all__ = ["router", "init_db"]