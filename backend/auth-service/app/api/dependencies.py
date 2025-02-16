# app/dependencies.py
from fastapi import Request, Depends

from app.config import settings
from app.exceptions import TokenMissing, TokenInvalid, UserNotExist, UserNotVerified, UserAlreadyVerified, \
    TokenVerificationFailed
from app.models.users import User
from app.repositories.redisRepository import RedisRepository
from app.repositories.tokensRepo import TokensRepository
from app.repositories.usersRepo import UsersRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.crypto import decode_jwt, decode_token_with_public_keys
from app.utils.key_manager import KeyManager


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository())


def get_token_service() -> TokenService:
    return TokenService(TokensRepository())


def get_email_service() -> EmailService:
    return EmailService(RedisRepository())


def get_key_manager() -> KeyManager:
    return KeyManager()


def get_refresh_token_from_req(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenMissing
    return token


def get_access_token_from_req(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise TokenMissing
    return token


async def get_current_auth_user(access_token: str = Depends(get_access_token_from_req),
                                auth_service: AuthService = Depends(get_auth_service),
                                key_manager: KeyManager = Depends(get_key_manager)) -> User | None:
    access_public_keys = key_manager.get_access_public_keys()
    decoded_access_token = decode_token_with_public_keys(access_token, access_public_keys)
    user_id = int(decoded_access_token.get("user_id"))
    if not decoded_access_token or not user_id:
        raise TokenInvalid
    user = await auth_service.users_repository.find_by_id(user_id)
    if not user:
        raise UserNotExist
    return user


async def get_current_verified_user(user: User = Depends(get_current_auth_user)) -> User:
    if not user.is_verified:
        raise UserNotVerified
    return user


async def get_current_unverified_user(user: User = Depends(get_current_auth_user)) -> User:
    if user.is_verified:
        raise UserAlreadyVerified
    return user


"""def verify_tokens_in_cookies(request: Request, key_manager: KeyManager = Depends(get_key_manager)):
    access_token = get_access_token_from_req(request)
    refresh_token = get_refresh_token_from_req(request)

    if not access_token or not refresh_token:
        raise TokenMissing

    access_public_keys = key_manager.get_access_public_keys()
    decoded_access_token = decode_token_with_public_keys(access_token, access_public_keys)

    refresh_public_keys = key_manager.get_refresh_public_keys()
    decoded_refresh_token = decode_token_with_public_keys(refresh_token, refresh_public_keys)

    if not decoded_access_token or not decoded_refresh_token:
        raise TokenVerificationFailed  # Если хотя бы один из токенов не был декодирован, ошибка

    return True  # Если оба токена успешно декодированы"""
