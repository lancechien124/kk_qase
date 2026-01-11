"""
Authentication Schemas
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    """User login request schema"""
    username: str
    password: str


class User(BaseModel):
    """User schema"""
    id: str
    username: str
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True

