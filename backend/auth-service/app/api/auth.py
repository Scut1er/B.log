from fastapi import APIRouter, Depends, Response, Query, Request, HTTPException

from app.api.dependencies import get_auth_service, get_email_service, get_token_service, verify_tokens_in_cookies, \
    get_current_user_id, get_refresh_token_from_req
from app.exceptions import UserNotVerified, EmailVerificationFailed, VerificationTokenInvalid, InvalidCredentials, \
    RegistrationFailed

from app.schemas import TokensResponse, RegisterRequest, LoginRequest
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.helpers import set_token_cookie

router = APIRouter()


@router.post("/register")
async def register_user(user_data: RegisterRequest,
                        response: Response,
                        auth_service: AuthService = Depends(get_auth_service),
                        email_service: EmailService = Depends(get_email_service)):
    user = await auth_service.register_user(email=user_data.email,
                                            password=user_data.password,
                                            fullname=user_data.fullname)
    if not user:
        raise RegistrationFailed
    # Генерация и отправка верификационного письма
    verification_token = await email_service.generate_email_verification_token(user.email)
    await email_service.send_email_verification(user.email, verification_token)

    return {"message": "User registered successfully. Please verify your email."}


@router.post("/login", response_model=TokensResponse)
async def login_user(user_data: LoginRequest,
                     response: Response,
                     auth_service: AuthService = Depends(get_auth_service),
                     token_service: TokenService = Depends(get_token_service)):
    user = await auth_service.login_user(email=user_data.email, password=user_data.password)
    if not user:
        raise InvalidCredentials
    if not user.is_verified:  # выдаем токены только верифицированным
        raise UserNotVerified

    # Генерируем токены для пользователя
    access_token = await token_service.generate_access_token(user.id)
    refresh_token = await token_service.generate_refresh_token(user.id)

    # Сеттим токены в куки
    set_token_cookie(response, "access", access_token)
    set_token_cookie(response, "refresh", refresh_token)

    return TokensResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout_user(response: Response,
                      request: Request,
                      verify_tokens: bool = Depends(verify_tokens_in_cookies),
                      token_service: TokenService = Depends(get_token_service)):
    refresh_token = get_refresh_token_from_req(request)
    await token_service.revoke_refresh_token(refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "User logged out successfully."}


@router.get("/verify-email")
async def verify_email(email: str = Query(...), token: str = Query(...),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    token_is_valid = await email_service.verify_email_verification_token(email, token)
    if not token_is_valid:
        raise VerificationTokenInvalid
    user_updated = await auth_service.users_repository.update_user_verification_status(email)
    if not user_updated:
        raise EmailVerificationFailed
    return {"message": "Email successfully verified"}


@router.get("/protected-endpoint")
async def protected_endpoint(current_user: int = Depends(get_current_user_id)):
    return {"message": "You have access to this endpoint", "user_id": current_user}
