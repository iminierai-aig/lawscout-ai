"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    tier: str
    search_count: int
    searches_remaining: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

class SearchTrack(BaseModel):
    query: str
    collection: Optional[str] = None
    result_count: Optional[int] = 0

class SearchLimitResponse(BaseModel):
    can_search: bool
    tier: str
    searches_remaining: int
    message: str