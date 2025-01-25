from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    fullname: Optional[str] = None


class UserResponseSchema(BaseModel):
    id: int
    email: str
    fullname: Optional[str]

    class Config:
        from_attributes = True


class RefreshTokenSchema(BaseModel):
    user_id: int
    token: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
