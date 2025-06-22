"""
OAuth 2.0 Endpoints for InstantDashboard

This module provides the actual API endpoints for Google OAuth authentication flow.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
import logging

from .oauth import oauth_handler, create_access_token, get_current_user, get_current_user_required, is_oauth_configured
from .models import Token, User

# Set up logging
logger = logging.getLogger(__name__)

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/config")
async def auth_config():
    """Get authentication configuration status."""
    return {
        "oauth_configured": is_oauth_configured(),
        "provider": "Google",
        "supports_demo_access": True,
        "demo_message": "Demo access available - full features with sample data",
        "login_required_message": "Sign in with Google for personalized data access"
    }


@router.get("/login")
async def login(request: Request, return_url: Optional[str] = None):
    """
    Initiate Google OAuth login flow.
    
    Query Parameters:
    - return_url: URL to redirect to after successful authentication
    """
    if not is_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OAuth not configured. Check GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables."
        )
    
    # Store return URL in state parameter (in production, use secure state management)
    state = return_url if return_url else "/"
    
    # Generate Google OAuth authorization URL
    auth_url = oauth_handler.get_authorization_url(state=state)
    
    logger.info(f"🚀 Redirecting to Google OAuth: {auth_url[:100]}...")
    
    # Redirect user to Google OAuth
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def oauth_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """
    Handle Google OAuth callback.
    
    This endpoint receives the authorization code from Google and exchanges it for tokens.
    """
    if error:
        logger.error(f"❌ OAuth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    try:
        # Exchange authorization code for tokens
        logger.info("🔄 Exchanging authorization code for tokens...")
        tokens = await oauth_handler.exchange_code_for_tokens(code)
        
        # Get user information from Google
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token not received from Google"
            )
        
        logger.info("📋 Fetching user information from Google...")
        google_user_info = await oauth_handler.get_user_info(access_token)
        
        # Create or update user in our system
        user = oauth_handler.create_or_update_user(google_user_info)
        
        # Create JWT token for our API
        token_data = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name
        }
        jwt_token = create_access_token(token_data)
        
        # Determine redirect URL
        return_url = state if state and state != "/" else "http://localhost:3000"
        
        logger.info(f"✅ OAuth flow completed for user: {user.email}")
        
        # In production, you might want to redirect to frontend with token in URL params
        # or set secure HTTP-only cookies. For this implementation, we'll return JSON.
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes
            "user": user.dict(),
            "redirect_url": return_url,
            "message": "Authentication successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Returns user profile and access level information.
    """
    logger.info(f"📋 User info requested for: {current_user.email}")
    return current_user


@router.get("/me/required", response_model=User)
async def get_current_user_info_required(current_user: User = Depends(get_current_user_required)):
    """
    Get current authenticated user information - authentication required.
    
    This endpoint requires valid authentication (no demo access).
    """
    logger.info(f"📋 Authenticated user info requested for: {current_user.email}")
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    In a stateless JWT system, logout is handled client-side by discarding the token.
    This endpoint provides a standard logout response.
    """
    logger.info("👋 User logout requested")
    return {
        "message": "Logged out successfully",
        "instructions": "Please discard your access token client-side"
    }


@router.get("/demo")
async def demo_access_info():
    """
    Information about demo access capabilities.
    """
    return {
        "demo_available": True,
        "demo_features": [
            "Natural language queries on sample data",
            "Chart generation and visualization",
            "Full pipeline: Query Planning → SQL → Results → Charts",
            "No personal data access"
        ],
        "demo_limitations": [
            "Sample dataset only (sticker sales data)",
            "No personal BigQuery project access",
            "Results cached and limited"
        ],
        "upgrade_benefits": [
            "Connect your own BigQuery projects",
            "Access your Google Analytics data",
            "Unlimited query volume",
            "Advanced features and customization"
        ]
    }


@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_user)):
    """
    Get authentication status and user access level.
    """
    return {
        "authenticated": current_user.is_authenticated,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "access_level": current_user.access_level,
        "has_bigquery_access": current_user.has_bigquery_access,
        "bigquery_project": current_user.bigquery_project_id,
        "features_available": {
            "demo_queries": True,
            "personal_data": current_user.has_bigquery_access,
            "advanced_features": current_user.access_level in ["premium", "enterprise"]
        }
    } 