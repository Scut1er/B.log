from datetime import datetime

from pydantic import BaseModel


class RefreshTokenSchema(BaseModel):
    user_id: int
    token: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True
