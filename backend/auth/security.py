"""Security utilities: Password hashing and JWT tokens"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import TokenData
import os

# Configuration - JWT_SECRET_KEY MUST be set in the environment.
# Fail closed: a missing/placeholder secret makes every token forgeable, so we
# refuse to start rather than silently signing with a publicly-known default.
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or SECRET_KEY.startswith("CHANGE_THIS"):
    raise RuntimeError(
        "JWT_SECRET_KEY is not set (or is still the placeholder). "
        "Generate one with `openssl rand -hex 32` and set it in the environment "
        "before starting the app."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Comma-separated list of admin emails, e.g. ADMIN_EMAILS="a@x.com,b@y.com"
ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.getenv("ADMIN_EMAILS", "").split(",")
    if e.strip()
}

FREE_TIER_LIMIT = 15
PRO_TIER_LIMIT = -1

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Authorize admin-only endpoints. A valid token is not enough — the caller
    must be on the ADMIN_EMAILS allowlist (broken function-level authorization)."""
    if current_user.email.lower() not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

def check_search_limit(user: User) -> tuple[bool, int, str]:
    if user.tier == "pro":
        return True, -1, "Unlimited searches (Pro tier)"

    searches_remaining = max(FREE_TIER_LIMIT - user.search_count, 0)

    if searches_remaining <= 0:
        return False, 0, "Free search limit reached. Upgrade to Pro for unlimited searches!"

    return True, searches_remaining, f"{searches_remaining} free searches remaining"


def reserve_search(db: Session, user: User) -> tuple[bool, int]:
    """Atomically reserve one search before running the costly RAG pipeline.

    The conditional UPDATE prevents concurrent requests from both passing the
    free-tier limit. Pro users are not incremented.
    """
    if user.tier == "pro":
        return True, -1

    updated = (
        db.query(User)
        .filter(
            User.id == user.id,
            User.tier == "free",
            User.search_count < FREE_TIER_LIMIT,
        )
        .update(
            {User.search_count: User.search_count + 1},
            synchronize_session=False,
        )
    )

    if updated != 1:
        db.rollback()
        db.refresh(user)
        return False, 0

    db.commit()
    db.refresh(user)
    return True, max(FREE_TIER_LIMIT - user.search_count, 0)


def refund_search(db: Session, user: User) -> None:
    """Return a reserved free-tier search when the search pipeline fails."""
    if user.tier == "pro":
        return

    (
        db.query(User)
        .filter(User.id == user.id, User.search_count > 0)
        .update(
            {User.search_count: User.search_count - 1},
            synchronize_session=False,
        )
    )
    db.commit()
    db.refresh(user)