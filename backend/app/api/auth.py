# backend/app/api/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import hashlib
import base64
import requests
from urllib.parse import quote

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserOnboarding
from app.config import settings

router = APIRouter()
security = HTTPBearer()

# ⚠️ Use Redis in prod
oauth_states = {}


# ---------- PKCE ----------
def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(96)
    ).decode().replace("=", "")

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().replace("=", "")

    return code_verifier, code_challenge


# ---------- AUTH ----------
@router.get("/auth/twitter/login")
def twitter_login(request: Request):
    if not settings.X_CLIENT_ID or not settings.X_CALLBACK_URL:
        raise HTTPException(status_code=500, detail="X OAuth not configured")

    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(32)

    oauth_states[state] = {
        "code_verifier": code_verifier,
        "created_at": datetime.utcnow()
    }

    auth_url = (
        "https://twitter.com/i/oauth2/authorize?"
        "response_type=code&"
        f"client_id={settings.X_CLIENT_ID}&"
        f"redirect_uri={quote(settings.X_CALLBACK_URL, safe='')}&"
        "scope=users.read%20tweet.read&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        "code_challenge_method=S256"
    )

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def twitter_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    if state not in oauth_states or "code_verifier" not in oauth_states[state]:
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/auth/error?message=Invalid+state+or+provider"
        )

    code_verifier = oauth_states[state]["code_verifier"]
    del oauth_states[state]

    # ---------- TOKEN EXCHANGE ----------
   

    # Build token request headers/data depending on whether a client secret is configured.
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.X_CALLBACK_URL,
        "code_verifier": code_verifier,
    }

    # If a client secret is configured, use HTTP Basic auth (client_id:client_secret).
    # If not, include the public client_id in the request body (PKCE public client flow).
    if getattr(settings, "X_CLIENT_SECRET", None):
        basic_auth = base64.b64encode(
            f"{settings.X_CLIENT_ID}:{settings.X_CLIENT_SECRET}".encode()
        ).decode()
        token_headers["Authorization"] = f"Basic {basic_auth}"
    else:
        token_data["client_id"] = settings.X_CLIENT_ID

    token_response = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        headers=token_headers,
        data=token_data,
    )


    if token_response.status_code != 200:
        print(f"DEBUG: Token exchange failed. Status: {token_response.status_code}, Response: {token_response.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Token exchange failed: {token_response.text}"
        )

    access_token = token_response.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token")

    # ---------- FETCH USER ----------
    user_response = requests.get(
        "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "user.fields": "profile_image_url,name,username"
        }
    )

    if user_response.status_code != 200:
        print(f"DEBUG: Fetch user failed. Status: {user_response.status_code}, Response: {user_response.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch X user: {user_response.text}"
        )

    twitter_user = user_response.json()["data"]

    # ---------- DB ----------
    twitter_id = twitter_user["id"]
    user = db.query(User).filter(User.twitter_id == twitter_id).first()

    if not user:
        # Use real email from Twitter if available, otherwise use placeholder
        email = twitter_user.get("email") or f"{twitter_user['username']}@twitter.placeholder"
        
        user = User(
            twitter_id=twitter_id,
            username=twitter_user["username"],
            email=email,
            display_name=twitter_user.get("name"),
            profile_image=twitter_user.get("profile_image_url"),
            preferences=[],
            keywords=[],
            alert_speed="instant",
            in_app_notifications=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new_user = True
    else:
        is_new_user = False

    # ---------- JWT ----------
    jwt_token = create_access_token({"sub": str(user.id)})

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/auth/callback"
        f"?token={jwt_token}&new_user={is_new_user}"
    )

# ---------- GOOGLE OAUTH ----------
@router.get("/auth/google/connect")
def google_connect(
    current_user: User = Depends(get_current_user),
):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CALLBACK_URL:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    state = secrets.token_urlsafe(32)
    # Store state and user_id to link account on callback
    oauth_states[state] = {
        "user_id": current_user.id,
        "created_at": datetime.utcnow()
    }

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={quote(settings.GOOGLE_CALLBACK_URL, safe='')}&"
        "scope=openid%20email%20profile&"
        f"state={state}&"
        "access_type=offline"
    )

    print(f"DEBUG: Google Auth URL: {auth_url}")
    return {"url": auth_url}


@router.get("/auth/google/callback")
def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    if state not in oauth_states:
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/auth/error?message=Invalid+state"
        )

    stored_state = oauth_states[state]
    user_id = stored_state.get("user_id")
    del oauth_states[state]

    # ---------- TOKEN EXCHANGE ----------
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_CALLBACK_URL,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data=token_data,
    )

    if token_response.status_code != 200:
         return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings?error=Google+connect+failed"
        )

    access_token = token_response.json().get("access_token")

    # ---------- FETCH USER ----------
    user_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if user_response.status_code != 200:
         return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings?error=Failed+to+fetch+Google+profile"
        )

    google_user = user_response.json()
    google_id = google_user.get("sub")
    google_email = google_user.get("email")

    if not google_id:
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings?error=No+Google+ID+found"
        )

    # ---------- LINK ACCOUNT ----------
    # Check if this google ID is already linked to ANOTHER user
    existing_link = db.query(User).filter(User.google_id == google_id).first()
    if existing_link and existing_link.id != user_id:
         return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings?error=Google+account+already+linked+to+another+user"
        )

    # Limit to linking only (user must be logged in to initiate)
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.google_id = google_id
            user.google_email = google_email
            # Optionally update email if not set? 
            # user.email = user.email or google_email 
            db.commit()
            return RedirectResponse(
                f"{settings.FRONTEND_URL}/settings?success=Google+account+connected"
            )

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/settings?error=User+not+found"
    )

# ---------- ME ----------
@router.get("/auth/me")
def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    return user


# ---------- ONBOARDING ----------
@router.post("/auth/onboarding")
def onboarding(
    data: UserOnboarding,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete onboarding by setting email, preferences, and alert settings"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is already taken by another user
    if data.email:
        existing_email = db.query(User).filter(
            User.email == data.email,
            User.id != user.id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already in use")
        
        user.email = data.email
    
    if data.telegram_id:
        user.telegram_chat_id = data.telegram_id
    
    if data.preferences:
        user.preferences = data.preferences
    
    if data.alert_speed in ['instant', '30mins', 'hourly']:
        user.alert_speed = data.alert_speed
    
    user.in_app_notifications = data.in_app_notifications
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Onboarding completed successfully",
        "user": user
    }
