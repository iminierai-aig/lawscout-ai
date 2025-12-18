"""OAuth authentication using Authlib"""
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from . import models, security
import os
import secrets
import logging

logger = logging.getLogger(__name__)

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

def get_oauth():
    """Get OAuth instance"""
    return oauth

async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise Exception("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build redirect URI - use explicit backend URL if set, otherwise use request URL
    # This fixes issues when behind a proxy/load balancer
    backend_url = os.getenv("BACKEND_URL", os.getenv("API_URL", ""))
    if backend_url:
        # Remove trailing slash if present
        backend_url = backend_url.rstrip('/')
        redirect_uri = f"{backend_url}/api/auth/google/callback"
    else:
        # Fallback to request URL (may not work behind proxy)
        redirect_uri = str(request.url_for('google_callback'))
    
    logger.info(f"OAuth redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

async def google_callback(request: Request, db: Session):
    """Handle Google OAuth callback"""
    # Verify state to prevent CSRF
    state = request.query_params.get('state')
    session_state = request.session.get('oauth_state')
    
    if not state or state != session_state:
        raise Exception("Invalid state parameter. Possible CSRF attack.")
    
    # Clear state from session
    request.session.pop('oauth_state', None)
    
    # Get token from Google
    token = await oauth.google.authorize_access_token(request)
    
    # Get user info from Google
    user_info = token.get('userinfo')
    if not user_info:
        # Fetch user info if not in token
        resp = await oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
    
    email = user_info.get('email')
    google_id = user_info.get('sub')  # Google's unique user ID
    full_name = user_info.get('name')
    profile_picture = user_info.get('picture')
    
    if not email:
        raise Exception("Email not provided by Google")
    
    # Check if user exists by email or google_id
    user = db.query(models.User).filter(
        (models.User.email == email) | (models.User.google_id == google_id)
    ).first()
    
    if user:
        # Update existing user with OAuth info if needed
        if not user.google_id:
            user.google_id = google_id
            user.oauth_provider = 'google'
        if profile_picture and not user.profile_picture:
            user.profile_picture = profile_picture
        if full_name and not user.full_name:
            user.full_name = full_name
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    else:
        # Create new user from OAuth
        from datetime import datetime
        user = models.User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            oauth_provider='google',
            profile_picture=profile_picture,
            hashed_password=None,  # OAuth users don't have passwords
            last_login=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token (same as email/password login)
    access_token = security.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier,
            "search_count": user.search_count,
            "searches_remaining": security.FREE_TIER_LIMIT - user.search_count if user.tier == "free" else -1,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "profile_picture": user.profile_picture
        }
    }

