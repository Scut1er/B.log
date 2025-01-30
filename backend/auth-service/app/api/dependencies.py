# app/dependencies.py
from fastapi import Request, Depends

from app.exceptions import TokenMissing, TokenInvalid
from app.repositories.redisRepository import RedisRepository
from app.repositories.tokensRepo import TokensRepository
from app.repositories.usersRepo import UsersRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.crypto import decode_access_jwt, decode_refresh_jwt


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository())


def get_token_service() -> TokenService:
    return TokenService(TokensRepository())


def get_email_service() -> EmailService:
    return EmailService(RedisRepository())


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


def verify_tokens_in_cookies(request: Request):
    access_token = get_access_token_from_req(request)
    refresh_token = get_refresh_token_from_req(request)

    if not access_token or not refresh_token:
        raise TokenMissing
    decode_access_jwt(access_token)
    decode_refresh_jwt(refresh_token)

    return True


def get_current_user_id(access_token: str = Depends(get_access_token_from_req)):
    decoded_access_token = decode_access_jwt(access_token)
    user_id = decoded_access_token.get("user_id")
    if not user_id:
        raise TokenInvalid
    return user_id
