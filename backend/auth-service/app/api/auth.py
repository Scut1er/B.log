from fastapi import APIRouter, Depends, Response

from app.config import settings
from app.repositories.tokensRepo import TokensRepository
from app.repositories.usersRepo import UsersRepository
from app.schemas import TokensResponse, RegisterRequest
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

router = APIRouter()


def get_auth_service() -> AuthService:
    users_repository = UsersRepository()
    return AuthService(users_repository)


def get_token_service() -> TokenService:
    tokens_repository = TokensRepository()
    return TokenService(tokens_repository)


@router.post("/register", response_model=TokensResponse)
async def register_user(user_data: RegisterRequest,
                        response: Response,
                        auth_service: AuthService = Depends(get_auth_service),
                        token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.register_user(email=user_data.email,
                                            password=user_data.password,
                                            fullname=user_data.fullname)
    # Генерируем токены для зарегистрированного пользователя
    access_token = await token_service.generate_access_token(user.id)
    refresh_token = await token_service.generate_refresh_token(user.id)

    # Сеттим токены в куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защищает от XSS
        secure=True,  # Требует HTTPS
        samesite="strict",  # Защита от CSRF
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES) * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES) * 60,
    )

    return TokensResponse(access_token=access_token, refresh_token=refresh_token)


