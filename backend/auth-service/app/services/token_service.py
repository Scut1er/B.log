from datetime import datetime, timezone, timedelta

from app.config import settings
from app.repositories.tokensRepo import TokensRepository
from app.schemas import RefreshTokenSchema, TokensSchema
from app.utils.crypto import decode_jwt, create_token


class TokenService:
    def __init__(self, token_repository: TokensRepository):
        self.token_repository: TokensRepository = token_repository

    async def generate_access_token(self, user_id: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES)
        return create_token(user_id, settings.ACCESS_PRIVATE_KEY, expires_at)

    async def generate_refresh_token(self, user_id: int, expires_at: datetime) -> str:
        return create_token(user_id, settings.REFRESH_PRIVATE_KEY, expires_at)

    async def refresh_access_token(self, refresh_token: str) -> TokensSchema:
        if not await (self.token_repository.is_refresh_token_valid(refresh_token)):
            raise Exception("Refresh token is invalid or expired")  # ИСПРАВИТЬ НА ОШИБКУ КАСТОМНУЮ!!!

        # Декодируем refresh-токен и получаем user_id
        payload = decode_jwt(refresh_token, settings.REFRESH_PUBLIC_KEY)
        user_id = int(payload["sub"])

        # Вычисляем expires_at (время истечения для нового refresh-токена)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES)

        new_refresh_token = await self.generate_refresh_token(user_id, expires_at)
        new_access_token = await self.generate_access_token(user_id)

        # Сохраняем новый refresh-токен в базе данных (вставка или обновление)
        await self.token_repository.save_refresh_token(user_id=user_id,
                                                       token=new_refresh_token,
                                                       expires_at=expires_at)
        return TokensSchema(access_token=new_access_token, refresh_token=new_refresh_token)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        await self.token_repository.delete_refresh_token(refresh_token)
