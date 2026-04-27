"""
用戶 Pydantic Schema
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用戶基礎 Schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None


class UserCreate(UserBase):
    """用戶創建 Schema"""
    password: str = Field(..., min_length=8)
    sendgrid_api_key: Optional[str] = None
    email_from_address: Optional[str] = None
    email_from_name: Optional[str] = None


class UserUpdate(BaseModel):
    """用戶更新 Schema"""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    email_from_address: Optional[str] = None
    email_from_name: Optional[str] = None


class UserResponse(UserBase):
    """用戶響應 Schema"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用戶登入 Schema"""
    username: str
    password: str


class Token(BaseModel):
    """令牌響應 Schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌數據 Schema"""
    user_id: Optional[int] = None
