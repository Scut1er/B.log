from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo, Field


class MessageResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters long")
    fullname: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str = Field(min_length=8, description="Password must be at least 8 characters long")

    @field_validator("new_password")
    @classmethod
    def passwords_must_differ(cls, new_password: str, info: ValidationInfo):
        old_password = info.data.get("old_password")
        if old_password == new_password:
            raise ValueError("New password must be different from the old password")
        return new_password


class ChangeEmailRequest(BaseModel):
    current_email: EmailStr
    password: str
    new_email: EmailStr

    @field_validator("new_email")
    @classmethod
    def email_must_differ(cls, new_email: EmailStr, info: ValidationInfo):
        current_email = info.data.get("current_email")
        if current_email == new_email:
            raise ValueError("New email must be different from the old email")
        return new_email


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
    message: str
