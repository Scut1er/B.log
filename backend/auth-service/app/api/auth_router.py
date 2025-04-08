from fastapi import APIRouter, Depends, Response, Query, Request

from app.api.dependencies import get_auth_service, get_email_service, get_token_service, \
    get_refresh_token_from_req, get_current_auth_user, get_current_verified_user, \
    get_current_unverified_user, get_key_manager, get_current_admin_user
from app.exceptions import VerificationTokenExpired, InvalidCredentials, \
    RegistrationFailed, InvalidEmail
from app.models.users import User

from app.schemas import RegisterRequest, LoginRequest, ChangePasswordRequest, MessageResponse, \
    ChangeEmailRequest, TokensResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.helpers import clear_token_cookies
from app.utils.key_manager import KeyManager

auth_router = APIRouter(prefix="/auth", tags=["Auth-service"], )


@auth_router.post("/register", response_model=TokensResponse,
                  summary="Register a new user",
                  description="Creates a new user with the specified email, password, and optional fullname. "
                              "After successful registration, a verification email is sent to the provided email address.")
async def register_user(user_data: RegisterRequest,
                        response: Response,
                        auth_service: AuthService = Depends(get_auth_service),
                        email_service: EmailService = Depends(get_email_service),
                        token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.register_user(email=user_data.email,
                                            password=user_data.password,
                                            fullname=user_data.fullname)
    if not user:
        raise RegistrationFailed

    await email_service.send_email_verification(user_data.email)

    access, refresh = await token_service.generate_tokens_cookies(user.id, response)
    return TokensResponse(access_token=access, refresh_token=refresh,
                          message="You were successfully registrated. Please verify your email", )


@auth_router.post("/login", response_model=TokensResponse,
                  summary="User login",
                  description="Authenticates a user using email and password. "
                              "Returns access and refresh tokens, which are also set in cookies.")
async def login_user(user_data: LoginRequest,
                     response: Response,
                     auth_service: AuthService = Depends(get_auth_service),
                     token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.login_user(email=user_data.email, password=user_data.password)
    if not user:
        raise InvalidCredentials

    access, refresh = await token_service.generate_tokens_cookies(user.id, response)
    return TokensResponse(access_token=access, refresh_token=refresh,
                          message="You have successfully entered your account")


@auth_router.post("/logout", response_model=MessageResponse,
                  summary="Logout",
                  description="Removes tokens from cookies and revokes the user's refresh token.")
async def logout_user(response: Response,
                      request: Request,
                      current_user: User = Depends(get_current_auth_user),
                      token_service: TokenService = Depends(get_token_service)):
    # Проверка аутентификации пользователя выполняется через зависимость get_current_auth_user
    refresh_token = get_refresh_token_from_req(request)
    await token_service.revoke_refresh_token(refresh_token)

    clear_token_cookies(response)

    return MessageResponse(message="User logged out successfully")


@auth_router.post("/change-password", response_model=MessageResponse,
                  summary="Change password",
                  description="Allows an authorized and verified user to change their password. "
                              "The current password must be provided.")
async def change_password(user_data: ChangePasswordRequest,
                          current_user: User = Depends(get_current_verified_user),
                          auth_service: AuthService = Depends(get_auth_service),
                          email_service: EmailService = Depends(get_email_service)):
    # Проверка верификации пользователя выполняется через зависимость get_current_verified_user
    if user_data.email != current_user.email:
        raise InvalidEmail

    await auth_service.change_password(user_data.email, user_data.old_password, user_data.new_password)

    # Отправка уведомления о смене пароля
    await email_service.send_password_change_notification(user_data.email)

    return MessageResponse(message="Password changed successfully.")


@auth_router.post("/change-email", response_model=MessageResponse,
                  summary="Change email",
                  description="Allows an authorized and verified user to change their email.")
async def change_email(user_data: ChangeEmailRequest,
                       current_user: User = Depends(get_current_verified_user),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    # Проверка верификации пользователя выполняется через зависимость get_current_verified_user
    if user_data.current_email != current_user.email:
        raise InvalidEmail

    # Изменение email и сброс статуса верификации
    await auth_service.change_email(user_data.password, user_data.current_email, user_data.new_email)

    # Отправка уведомления на старый email о смене почты
    await email_service.send_email_change_notification(user_data.current_email, user_data.new_email)
    # Отправка письма с верификацией на новый email
    await email_service.send_email_verification(user_data.new_email)

    return MessageResponse(message="Email successfully changed.")


@auth_router.post("/send-verification-email", response_model=MessageResponse,
                  summary="Send email verification",
                  description="Sends an email with a verification token to users "
                              "whose accounts are not yet verified.")
async def send_verification_email(email: str,
                                  email_service: EmailService = Depends(get_email_service),
                                  current_user: User = Depends(get_current_unverified_user)):
    # НУЖНО ОГРАНИЧИТЬ ВОЗМОЖНОСТЬ ОТПРАВКИ ЗАПРОСА, ВОЗМОЖНО ЧЕРЕЗ nginx
    # Проверка отсутствия верификации пользователя выполняется через зависимость get_current_unverified_user
    if email != current_user.email:
        raise InvalidEmail
    await email_service.send_email_verification(email)

    return MessageResponse(message="Verification token has been sent to your email.")


@auth_router.get("/verify-email", response_model=MessageResponse,
                 summary="Verify email",
                 description="Verifies the user's email using the token received by email.")
async def verify_email(email: str = Query(...), token: str = Query(...),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    token_is_valid = await email_service.verify_email_verification_token(email, token)
    if not token_is_valid:
        raise VerificationTokenExpired

    await auth_service.verify_user_by_email(email)
    return MessageResponse(message="Email successfully verified")


@auth_router.get("/protected-auth-endpoint", response_model=MessageResponse,
                 summary="Access for authorized users",
                 description="Endpoint accessible only to authorized users.")
async def protected_auth_endpoint(current_user: User = Depends(get_current_auth_user)):
    # Проверка аутентификации пользователя выполняется через зависимость get_current_auth_user
    return MessageResponse(message="You have access to authorized endpoint")


@auth_router.get("/protected-verify-endpoint", response_model=MessageResponse,
                 summary="Access for verified users",
                 description="Endpoint accessible only to users with verified email.")
async def protected_verify_endpoint(current_user: User = Depends(get_current_verified_user)):
    # Проверка верификации пользователя выполняется через зависимость get_current_verified_user
    return MessageResponse(message="You have access to verified endpoint")


@auth_router.post("/rotate-keys", summary="Rotate JWT keys")
async def rotate_keys(key_manager: KeyManager = Depends(get_key_manager),
                      current_admin_user: User = Depends(get_current_admin_user)):
    key_manager.rotate_keys()
    return MessageResponse(message="🔑 Ключи успешно обновлены")
