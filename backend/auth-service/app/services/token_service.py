from app.config import settings
from app.utils.crypto import decode_jwt, create_token


class TokenService:
    @staticmethod
    def generate_access_token(user_id: int) -> str:
        return create_token(user_id, settings.ACCESS_PRIVATE_KEY,
                            settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES)

    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        return create_token(user_id, settings.REFRESH_PRIVATE_KEY,
                            settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES)

    @staticmethod
    def verify_access_token(token: str) -> dict:
        return decode_jwt(token, settings.ACCESS_PUBLIC_KEY)

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        return decode_jwt(token, settings.REFRESH_PUBLIC_KEY)

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """мб исправить добавить обработку оишбок"""
        payload = TokenService.verify_refresh_token(refresh_token)
        return TokenService.generate_access_token(payload["sub"])
