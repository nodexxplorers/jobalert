# backend/app/api/auth.py (Using Authlib for Twitter OAuth)

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import OAuth2Client as OAuth2Session
import httpx
from datetime import datetime
import tweepy
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.models.user import User
from app.config import settings

router = APIRouter()
security = HTTPBearer()

# OAuth state storage (use Redis in production)
oauth_states = {}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.get("/auth/twitter/login")
def twitter_login(request: Request):
    """
    Step 1: Redirect user to X OAuth page
    User clicks "Sign in with X" → calls this endpoint
    """
    try:
        # Verbose Logging for Debugging
        print("--- Twitter OAuth Debug ---")
        print(f"Client ID: {settings.X_CLIENT_ID[:5]}...{settings.X_CLIENT_ID[-5:]}")
        print(f"Redirect URI: {settings.X_CALLBACK_URL}")
        print(f"Scopes: {['users.read', 'tweet.read']}")
        print("---------------------------")

        # Create OAuth2 session with Authlib
        session = OAuth2Session(
            client_id=settings.X_CLIENT_ID,
            client_secret=settings.X_CLIENT_SECRET,
            redirect_uri=settings.X_CALLBACK_URL,
            scope=["users.read", "tweet.read"],
        )
        
        # Generate authorization URL
        auth_url, state = session.create_authorization_url(
            "https://twitter.com/i/oauth2/authorize",
            code_challenge_method="S256"
        )
        
        print(f"Generated Auth URL: {auth_url}")
        
        # Store state for CSRF protection
        request.session["oauth_state"] = state
        
        # Redirect to Twitter
        return RedirectResponse(auth_url)
    
    except Exception as e:
        print(f"Twitter login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/callback")
async def twitter_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Step 2: X redirects back with authorization code
    Exchange code for access token and get user info
    """
    try:
        # Verify state (CSRF protection)
        stored_state = request.session.get("oauth_state")
        if not stored_state or stored_state != state:
            error_url = f"{settings.FRONTEND_URL}/auth/error?message=Invalid+state"
            return RedirectResponse(error_url)
        
        # Create new OAuth2 session for token exchange
        session = OAuth2Session(
            client_id=settings.X_CLIENT_ID,
            client_secret=settings.X_CLIENT_SECRET,
            redirect_uri=settings.X_CALLBACK_URL,
            scope=["tweet.read", "users.read"],
        )
        
        # Exchange authorization code for access token
        # Using standard api.twitter.com endpoint
        token = session.fetch_token(
            "https://api.twitter.com/2/oauth2/token",
            code=code,
            # For confidential clients, secret must be provided
            client_id=settings.X_CLIENT_ID,
            client_secret=settings.X_CLIENT_SECRET
        )
        
        # Get access token
        access_token = token.get("access_token")
        if not access_token:
            raise ValueError("Failed to get access token")
        
        # Get user info from X API
        client = tweepy.Client(bearer_token=access_token)
        me = client.get_me(user_fields=['profile_image_url', 'username', 'name'])
        
        # Validate response
        if not me or not me.data:  # type: ignore
            raise ValueError("Failed to get user info from X")
        
        twitter_user = me.data  # type: ignore
        
        # Check if user exists
        twitter_id_str = str(twitter_user.id)
        user = db.query(User).filter(User.twitter_id == twitter_id_str).first()
        
        if not user:
            # Create new user
            user = User(
                twitter_id=str(twitter_user.id),
                username=twitter_user.username,
                email=f"{twitter_user.username}@twitter.placeholder",
                display_name=twitter_user.name if hasattr(twitter_user, 'name') else twitter_user.username,
                profile_image=twitter_user.profile_image_url if hasattr(twitter_user, 'profile_image_url') else None,
                preferences=[],
                keywords=[],
                alert_speed='instant',
                in_app_notifications=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
        else:
            is_new_user = False
        
        # Create JWT token
        jwt_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token
        # Note: frontend needs to handle 'new_user' if applicable
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}&new_user={is_new_user}"
        return RedirectResponse(redirect_url)
    
    except Exception as e:
        print(f"OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        
        error_message = str(e).replace(' ', '+')
        error_url = f"{settings.FRONTEND_URL}/auth/error?message={error_message}"
        return RedirectResponse(error_url)


@router.get("/auth/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user info from JWT token in Authorization header
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "profile_image": current_user.profile_image,
        "preferences": current_user.preferences,
        "created_at": current_user.created_at
    }