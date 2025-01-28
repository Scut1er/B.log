from datetime import datetime, timezone, timedelta

from app.config import settings
from app.repositories.tokensRepo import TokensRepository
from app.utils.crypto import create_jwt_token, decode_refresh_jwt


class TokenService:
    def __init__(self, token_repository: TokensRepository):
        self.token_repository: TokensRepository = token_repository

    async def generate_access_token(self, user_id: int) -> str:
        expires_at = (datetime.now(timezone.utc) + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES))).replace(tzinfo=None)
        return create_jwt_token(user_id=user_id, token_type="access",
                                private_key=settings.ACCESS_PRIVATE_KEY, expires_at=expires_at)

    async def generate_refresh_token(self, user_id: int) -> str:
        expires_at = (datetime.now(timezone.utc) + timedelta(
            minutes=int(settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES))).replace(tzinfo=None)
        refresh_token = create_jwt_token(user_id=user_id, token_type="refresh",
                                         private_key=settings.REFRESH_PRIVATE_KEY, expires_at=expires_at)
        await self.token_repository.save_refresh_token(user_id, refresh_token, expires_at)
        return refresh_token

    async def refresh_access_token(self, refresh_token: str) -> str:
        if not await (self.token_repository.is_refresh_token_valid(refresh_token)):
            raise Exception("Refresh token is invalid or expired")  # ИСПРАВИТЬ НА ОШИБКУ КАСТОМНУЮ!!!

        # Декодируем refresh-токен и получаем user_id
        payload = decode_refresh_jwt(refresh_token)
        user_id = int(payload["user_id"])

        new_access_token = await self.generate_access_token(user_id)
        return new_access_token

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        await self.token_repository.delete_refresh_token(refresh_token)

