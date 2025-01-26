from fastapi import APIRouter, Depends, Response

from app.config import settings
from app.repositories.tokensRepo import TokensRepository
from app.repositories.usersRepo import UsersRepository
from app.schemas import TokensResponse, RegisterRequest, LoginRequest
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.utils.helpers import set_token_cookie

router = APIRouter()


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository())


def get_token_service() -> TokenService:
    return TokenService(TokensRepository())


@router.post("/register", response_model=TokensResponse)
async def register_user(user_data: RegisterRequest,
                        response: Response,
                        auth_service: AuthService = Depends(get_auth_service),
                        token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.register_user(email=user_data.email,
                                            password=user_data.password,
                                            fullname=user_data.fullname)
    # После успешной регистрации автоматически логиним пользователя
    return await login_user(
        user_data=user_data,
        response=response,
        auth_service=auth_service,
        token_service=token_service,
    )


@router.post("/login", response_model=TokensResponse)
async def login_user(user_data: LoginRequest,
                     response: Response,
                     auth_service: AuthService = Depends(get_auth_service),
                     token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.login_user(email=user_data.email, password=user_data.password)

    # Генерируем токены для пользователя
    access_token = await token_service.generate_access_token(user.id)
    refresh_token = await token_service.generate_refresh_token(user.id)

    # Сеттим токены в куки
    set_token_cookie(response, "access", access_token)
    set_token_cookie(response, "refresh", refresh_token)

    return TokensResponse(access_token=access_token, refresh_token=refresh_token)
