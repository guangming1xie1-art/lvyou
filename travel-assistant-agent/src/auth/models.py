"""
Authentication related data models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class User(BaseModel):
    """User model"""
    id: str
    username: str
    # email: EmailStr
    is_active: bool = True
    # created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('username')
    def validate_username(cls, v, values):
        """Validate username is not in password"""
        if 'password' in values:
            password = values['password']
            if v.lower() in password.lower():
                raise ValueError('Password must not contain username')
        return v


class UserRegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class TokenRequest(BaseModel):
    """Token request (login)"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response"""
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Login response with user info and tokens"""
    user: UserResponse
    tokens: TokenResponse
