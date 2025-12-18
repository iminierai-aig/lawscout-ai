"""FastAPI routes for authentication"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from starlette.middleware.sessions import SessionMiddleware
from . import models, schemas, security
from .database import get_db
import os

# Optional OAuth import (only if oauth.py exists)
try:
    from . import oauth
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    oauth = None

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = security.get_user_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(user_create.password)
    db_user = models.User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = security.create_access_token(data={"sub": db_user.email})
    
    user_response = schemas.UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        tier=db_user.tier,
        search_count=db_user.search_count,
        searches_remaining=security.FREE_TIER_LIMIT,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        last_login=db_user.last_login
    )
    
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = security.create_access_token(data={"sub": user.email})
    searches_remaining = security.FREE_TIER_LIMIT - user.search_count if user.tier == "free" else -1
    
    user_response = schemas.UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        tier=user.tier,
        search_count=user.search_count,
        searches_remaining=searches_remaining,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
        profile_picture=user.profile_picture
    )
    
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    searches_remaining = security.FREE_TIER_LIMIT - current_user.search_count if current_user.tier == "free" else -1
    
    return schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tier=current_user.tier,
        search_count=current_user.search_count,
        searches_remaining=searches_remaining,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        profile_picture=current_user.profile_picture
    )

@router.get("/search/check-limit", response_model=schemas.SearchLimitResponse)
async def check_search_limit(
    current_user: models.User = Depends(security.get_current_active_user)
):
    can_search, searches_remaining, message = security.check_search_limit(current_user)
    
    if not can_search:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )
    
    return schemas.SearchLimitResponse(
        can_search=can_search,
        tier=current_user.tier,
        searches_remaining=searches_remaining,
        message=message
    )

@router.post("/search/track")
async def track_search(
    search_data: schemas.SearchTrack,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    can_search, searches_remaining, message = security.check_search_limit(current_user)
    
    if not can_search:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )
    
    search_record = models.SearchHistory(
        user_id=current_user.id,
        query=search_data.query,
        collection=search_data.collection,
        result_count=search_data.result_count
    )
    db.add(search_record)
    
    current_user.search_count += 1
    db.commit()
    
    new_searches_remaining = security.FREE_TIER_LIMIT - current_user.search_count if current_user.tier == "free" else -1
    
    return {
        "message": "Search tracked successfully",
        "search_count": current_user.search_count,
        "searches_remaining": new_searches_remaining
    }

@router.post("/admin/upgrade-user")
async def upgrade_user_to_pro(email: str, db: Session = Depends(get_db)):
    user = security.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.tier = "pro"
    db.commit()
    
    return {"message": f"User {email} upgraded to Pro tier"}

@router.get("/admin/stats")
async def get_platform_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Basic counts
    total_users = db.query(models.User).count()
    pro_users = db.query(models.User).filter(models.User.tier == "pro").count()
    free_users = total_users - pro_users
    total_searches = db.query(models.SearchHistory).count()
    
    # Users at free tier limit
    users_at_limit = db.query(models.User).filter(
        and_(
            models.User.tier == "free",
            models.User.search_count >= security.FREE_TIER_LIMIT
        )
    ).count()
    
    # OAuth statistics
    oauth_users = db.query(models.User).filter(models.User.oauth_provider.isnot(None)).count()
    email_users = db.query(models.User).filter(models.User.oauth_provider.is_(None)).count()
    
    # Users by OAuth provider
    google_users = db.query(models.User).filter(models.User.oauth_provider == "google").count()
    github_users = db.query(models.User).filter(models.User.oauth_provider == "github").count()
    
    # Active users (logged in within last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(models.User).filter(
        models.User.last_login >= thirty_days_ago
    ).count()
    
    # Recent sign-ups (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups = db.query(models.User).filter(
        models.User.created_at >= seven_days_ago
    ).count()
    
    # Recent sign-ups by method
    recent_oauth = db.query(models.User).filter(
        and_(
            models.User.created_at >= seven_days_ago,
            models.User.oauth_provider.isnot(None)
        )
    ).count()
    recent_email = db.query(models.User).filter(
        and_(
            models.User.created_at >= seven_days_ago,
            models.User.oauth_provider.is_(None)
        )
    ).count()
    
    return {
        "total_users": total_users,
        "free_users": free_users,
        "pro_users": pro_users,
        "total_searches": total_searches,
        "users_at_limit": users_at_limit,
        "conversion_opportunity": users_at_limit,
        # Sign-in method statistics
        "oauth_users": oauth_users,
        "email_users": email_users,
        "google_users": google_users,
        "github_users": github_users,
        # Activity statistics
        "active_users_30d": active_users,
        "recent_signups_7d": recent_signups,
        "recent_oauth_signups_7d": recent_oauth,
        "recent_email_signups_7d": recent_email
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for auth service"""
    return {"status": "healthy", "service": "auth"}

# OAuth Routes (only if OAuth is available)
if OAUTH_AVAILABLE:
    @router.get("/google/login", name="google_login")
    async def google_login_route(request: Request):
        """Initiate Google OAuth login"""
        try:
            return await oauth.google_login(request)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OAuth login failed: {str(e)}"
            )

    @router.get("/google/callback", name="google_callback")
    async def google_callback_route(request: Request, db: Session = Depends(get_db)):
        """Handle Google OAuth callback"""
        try:
            result = await oauth.google_callback(request, db)
            
            # Redirect to frontend with token in URL (frontend will extract it)
            # In production, you might want to use a more secure method like httpOnly cookies
            frontend_url = os.getenv("FRONTEND_URL", "https://lawscoutai.com")
            token = result["access_token"]
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?token={token}&provider=google"
            )
        except Exception as e:
            # Redirect to frontend with error
            frontend_url = os.getenv("FRONTEND_URL", "https://lawscoutai.com")
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?error={str(e)}"
            )