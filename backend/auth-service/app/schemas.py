from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    fullname: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def passwords_must_differ(cls, new_password: str, info: ValidationInfo):
        old_password = info.data.get("old_password")
        if old_password == new_password:
            raise ValueError("New password must be different from the old password")
        return new_password


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
