from fastapi import APIRouter, Depends, Response, Query, Request

from app.api.dependencies import get_auth_service, get_email_service, get_token_service, \
    get_refresh_token_from_req, get_current_auth_user, get_current_verified_user, \
    get_current_unverified_user
from app.exceptions import EmailVerificationFailed, VerificationTokenExpired, InvalidCredentials, \
    RegistrationFailed, UserAlreadyVerified, InvalidEmail
from app.models.users import User

from app.schemas import TokensResponse, RegisterRequest, LoginRequest, ChangePasswordRequest, MessageResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.helpers import set_token_cookie, clear_token_cookies

router = APIRouter(prefix="/auth", tags=["Auth-service"], )


@router.post("/register", response_model=MessageResponse,
             summary="Регистрация нового пользователя",
             description="Создаёт нового пользователя с указанным email, паролем и полным именем (опционально). "
                         "После успешной регистрации на указанный email отправляется письмо для подтверждения.")
async def register_user(user_data: RegisterRequest,
                        auth_service: AuthService = Depends(get_auth_service),
                        email_service: EmailService = Depends(get_email_service)):
    user = await auth_service.register_user(email=user_data.email,
                                            password=user_data.password,
                                            fullname=user_data.fullname)
    if not user:
        raise RegistrationFailed

    await email_service.send_email_verification(user_data.email)
    return {"message": "User registered successfully. Please verify your email."}


@router.post("/login", response_model=TokensResponse,
             summary="Авторизация пользователя",
             description="Аутентифицирует пользователя с использованием email и пароля. "
                         "Возвращает access и refresh токены, которые также устанавливаются в cookies.")
async def login_user(user_data: LoginRequest,
                     response: Response,
                     auth_service: AuthService = Depends(get_auth_service),
                     token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.login_user(email=user_data.email, password=user_data.password)
    if not user:
        raise InvalidCredentials

    # Генерируем токены для пользователя
    access_token = await token_service.generate_access_token(user.id)
    refresh_token = await token_service.generate_refresh_token(user.id)

    # Сеттим токены в куки
    set_token_cookie(response, "access", access_token)
    set_token_cookie(response, "refresh", refresh_token)

    return TokensResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse,
             summary="Выход из системы",
             description="Удаляет токены из cookies и аннулирует refresh токен пользователя.")
async def logout_user(response: Response,
                      request: Request,
                      current_user: User = Depends(get_current_auth_user),
                      token_service: TokenService = Depends(get_token_service)):
    refresh_token = get_refresh_token_from_req(request)
    await token_service.revoke_refresh_token(refresh_token)

    clear_token_cookies(response)

    return {"message": "User logged out successfully."}


@router.post("/change-password", response_model=MessageResponse,
             summary="Смена пароля",
             description="Позволяет авторизованному и верифицированному пользователю изменить свой пароль. "
                         "Требуется указание текущего пароля.")
async def change_password(user_data: ChangePasswordRequest,
                          current_user: User = Depends(get_current_verified_user),
                          auth_service: AuthService = Depends(get_auth_service),
                          email_service: EmailService = Depends(get_email_service)):
    # верификация пользователя проверена через зависимость get_current_verified_user
    if user_data.email != current_user.email:
        raise InvalidEmail

    user = await auth_service.login_user(user_data.email, user_data.old_password)  # Проверяем старый пароль
    if not user:
        raise InvalidCredentials

    await auth_service.change_password(user_data.email, user_data.new_password)

    # Отправляем уведомление пользователю
    await email_service.send_password_change_notification(user.email)

    return {"message": "Password changed successfully."}


@router.post("/send-verification-email", response_model=MessageResponse,
             summary="Отправка письма для подтверждения email",
             description="Отправляет письмо с токеном для подтверждения email пользователям, "
                         "чьи аккаунты ещё не верифицированы.")
async def send_verification_email(email_service: EmailService = Depends(get_email_service),
                                  current_user: User = Depends(get_current_unverified_user)):
    recipient_email = current_user.email
    # Отправка нового токена
    await email_service.send_email_verification(recipient_email)

    return {"message": "Verification token has been sent to your email."}


@router.get("/verify-email", response_model=MessageResponse,
            summary="Подтверждение email",
            description="Подтверждает email пользователя с использованием токена, полученного на почту.")
async def verify_email(email: str = Query(...), token: str = Query(...),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    user = await auth_service.users_repository.find_by_email(email)
    if not user:
        raise EmailVerificationFailed(detail="User not found. Try /send-verification-email again")
    if user.is_verified:
        raise UserAlreadyVerified
    token_is_valid = await email_service.verify_email_verification_token(email, token)
    if not token_is_valid:
        raise VerificationTokenExpired
    user_updated = await auth_service.users_repository.update_verification_status(email)
    if not user_updated:
        raise EmailVerificationFailed
    return {"message": "Email successfully verified"}


@router.get("/protected-auth-endpoint", response_model=MessageResponse,
            summary="Доступ для авторизованных пользователей",
            description="Эндпоинт, доступный только авторизованным пользователям.")
async def protected_auth_endpoint(current_user: User = Depends(get_current_auth_user)):
    return {"message": "You have access to authorized endpoint", "user": current_user}


@router.get("/protected-verify-endpoint", response_model=MessageResponse,
            summary="Доступ для верифицированных пользователей",
            description="Эндпоинт, доступный только пользователям с подтверждённым email.")
async def protected_verify_endpoint(current_user: User = Depends(get_current_verified_user)):
    return {"message": "You have access to verified endpoint", "user": current_user}
