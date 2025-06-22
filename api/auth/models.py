"""
Authentication models for OAuth 2.0 and user management.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    """User model for authenticated users."""
    user_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    is_authenticated: bool = True
    google_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # User preferences and settings
    preferences: dict = {}
    
    # Access level - could be: demo, basic, premium, enterprise
    access_level: str = "basic"
    
    # BigQuery access - for multi-tenant data access
    has_bigquery_access: bool = False
    bigquery_project_id: Optional[str] = None


class UserCreate(BaseModel):
    """Model for creating new users from OAuth."""
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: str


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class TokenData(BaseModel):
    """Token data for JWT validation."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    exp: Optional[int] = None 