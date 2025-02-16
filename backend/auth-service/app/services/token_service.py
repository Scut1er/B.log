from datetime import datetime, timezone, timedelta

from app.config import settings
from app.exceptions import RefreshTokenInvalid
from app.repositories.tokensRepo import TokensRepository
from app.utils.crypto import create_jwt_token, decode_token_with_public_keys
from app.utils.helpers import set_token_cookie
from app.utils.key_manager import KeyManager


class TokenService:
    def __init__(self, token_repository: TokensRepository):
        self.token_repository: TokensRepository = token_repository
        self.key_manager = KeyManager()

    async def generate_access_token(self, user_id: int) -> str:
        expires_at = (datetime.now(timezone.utc) + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES))).replace(tzinfo=None)
        private_key = self.key_manager.get_access_private_key()
        return create_jwt_token(user_id=user_id, token_type="access",
                                private_key=private_key, expires_at=expires_at)

    async def generate_refresh_token(self, user_id: int) -> str:
        expires_at = (datetime.now(timezone.utc) + timedelta(
            minutes=int(settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES))).replace(tzinfo=None)
        private_key = self.key_manager.get_refresh_private_key()
        refresh_token = create_jwt_token(user_id=user_id, token_type="refresh",
                                         private_key=private_key, expires_at=expires_at)
        await self.token_repository.save_refresh_token(user_id, refresh_token, expires_at)
        return refresh_token

    async def get_or_create_refresh_token(self, user_id):
        """Проверяет существование и валидность Refresh-токена.
        Если токен не существует или недействителен, создаёт новый."""
        existing_token_record = await self.token_repository.get_refresh_token_by_user_id(user_id)

        if existing_token_record:
            is_valid = await self.token_repository.is_refresh_token_valid(existing_token_record.token)
            if is_valid:
                return existing_token_record.token
            raise RefreshTokenInvalid

        # Создаёт новый refresh-токен, если старый не найден
        return await self.generate_refresh_token(user_id)

    async def generate_tokens_cookies(self, user_id, response):
        # Генерирует токены для пользователя
        access_token = await self.generate_access_token(user_id)
        refresh_token = await self.get_or_create_refresh_token(user_id)

        # Устанавливает токены в cookies
        set_token_cookie(response, "access", access_token)
        set_token_cookie(response, "refresh", refresh_token)

        return access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> str:
        if not await (self.token_repository.is_refresh_token_valid(refresh_token)):
            raise RefreshTokenInvalid

        # Декодируем refresh-токен previous и current public ключами
        public_keys = self.key_manager.get_refresh_public_keys()
        payload = decode_token_with_public_keys(refresh_token, public_keys)

        if not payload:
            raise RefreshTokenInvalid

        user_id = int(payload["user_id"])
        new_access_token = await self.generate_access_token(user_id)
        return new_access_token

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        await self.token_repository.delete_refresh_token(refresh_token)
