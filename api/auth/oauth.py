"""
OAuth 2.0 Authentication Handler for InstantDashboard

This module implements real Google OAuth 2.0 authentication with JWT token management.
Replaces the placeholder authentication with production-ready security.
"""

import os
import json
import jwt
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import logging

from .models import User, UserCreate, Token, TokenData

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer(auto_error=False)

# OAuth settings from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") 
REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8001/auth/callback")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Google OAuth URLs
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# In-memory user storage (in production, use a real database)
# This will store users by their Google ID for this implementation
users_db: Dict[str, User] = {}


class OAuthHandler:
    """Handles Google OAuth 2.0 authentication flow."""
    
    def __init__(self):
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("⚠️ Google OAuth credentials not configured properly")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GOOGLE_AUTHORIZATION_URL}?{param_string}"
    
    async def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens."""
        try:
            # Exchange code for tokens
            token_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }
            
            response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
            response.raise_for_status()
            
            tokens = response.json()
            logger.info("✅ Successfully exchanged authorization code for tokens")
            
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Token exchange failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google using access token."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"✅ Retrieved user info for: {user_info.get('email')}")
            
            return user_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user information: {str(e)}"
            )
    
    def create_or_update_user(self, google_user_info: Dict[str, Any]) -> User:
        """Create or update user from Google OAuth data."""
        google_id = google_user_info.get("id")
        email = google_user_info.get("email")
        name = google_user_info.get("name", email)
        picture = google_user_info.get("picture")
        
        # Check if user exists
        if google_id in users_db:
            # Update existing user
            user = users_db[google_id]
            user.last_login = datetime.now()
            user.name = name  # Update name in case it changed
            user.picture = picture  # Update picture
            logger.info(f"✅ Updated existing user: {email}")
        else:
            # Create new user
            user = User(
                user_id=google_id,
                email=email,
                name=name,
                picture=picture,
                google_id=google_id,
                created_at=datetime.now(),
                last_login=datetime.now(),
                access_level="basic",  # Default access level
                has_bigquery_access=False  # Will be configured per user
            )
            users_db[google_id] = user
            logger.info(f"✅ Created new user: {email}")
        
        return user


# Create OAuth handler instance
oauth_handler = OAuthHandler()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Created JWT token for user: {data.get('user_id', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ JWT encoding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )


def verify_access_token(token: str) -> TokenData:
    """Verify and decode JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        token_data = TokenData(user_id=user_id, email=email, exp=payload.get("exp"))
        return token_data
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        logger.error(f"❌ JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token.
    
    This replaces the placeholder function in main.py with real authentication.
    """
    # Handle case where no credentials provided (optional auth)
    if not credentials:
        # Return anonymous/demo user for unauthenticated access
        return User(
            user_id="anonymous",
            email="demo@example.com",
            name="Anonymous User",
            is_authenticated=False,
            access_level="demo",
            has_bigquery_access=False
        )
    
    # Verify the token
    token_data = verify_access_token(credentials.credentials)
    
    # Get user from our storage
    user = users_db.get(token_data.user_id)
    if not user:
        logger.error(f"❌ User not found for token: {token_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"✅ Authenticated user: {user.email}")
    return user


async def get_current_user_required(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user - authentication required.
    
    Use this for endpoints that require authentication.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return await get_current_user(credentials)


# Helper function to check if OAuth is properly configured
def is_oauth_configured() -> bool:
    """Check if OAuth environment variables are properly set."""
    return all([
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        SECRET_KEY != "your-secret-key-here"
    ])


# Helper function for demo access
def get_demo_user() -> User:
    """Get demo user for unauthenticated access."""
    return User(
        user_id="demo",
        email="demo@instantdashboard.com",
        name="Demo User",
        is_authenticated=False,
        access_level="demo",
        has_bigquery_access=True,  # Demo user can access demo dataset
        bigquery_project_id=os.getenv("BQ_PROJECT_ID")  # Use demo project
    ) 