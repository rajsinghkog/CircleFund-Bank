from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    id: Optional[str] = None
    name: str
    phone: str
    created_at: Optional[datetime] = None

class UserCreate(UserBase):
    # Password removed in simplified auth-less flow
    password: str | None = None

class UserLogin(BaseModel):
    phone: str
    # Password removed
    password: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    phone: Optional[str] = None
