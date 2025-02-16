from fastapi import APIRouter, Depends, Response, Query, Request

from app.api.dependencies import get_auth_service, get_email_service, get_token_service, \
    get_refresh_token_from_req, get_current_auth_user, get_current_verified_user, \
    get_current_unverified_user
from app.exceptions import VerificationTokenExpired, InvalidCredentials, \
    RegistrationFailed, InvalidEmail, UserNotVerified
from app.models.users import User

from app.schemas import TokensResponse, RegisterRequest, LoginRequest, ChangePasswordRequest, MessageResponse, \
    ChangeEmailRequest
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.utils.helpers import clear_token_cookies

router = APIRouter(prefix="/auth", tags=["Auth-service"], )


@router.post("/register", response_model=MessageResponse,
             summary="Register a new user",
             description="Creates a new user with the specified email, password, and optional full name. "
                         "After successful registration, a verification email is sent to the provided email address.")
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
    if not user.is_verified:
        raise UserNotVerified

    access, refresh = await token_service.generate_tokens_cookies(user.id, response)
    return TokensResponse(access_token=access,
                          refresh_token=refresh)


@router.post("/logout", response_model=MessageResponse,
             summary="Logout",
             description="Removes tokens from cookies and revokes the user's refresh token.")
async def logout_user(response: Response,
                      request: Request,
                      current_user: User = Depends(get_current_auth_user),
                      token_service: TokenService = Depends(get_token_service)):
    refresh_token = get_refresh_token_from_req(request)
    await token_service.revoke_refresh_token(refresh_token)

    clear_token_cookies(response)

    return {"message": "User logged out successfully."}


@router.post("/change-password", response_model=MessageResponse,
             summary="Change password",
             description="Allows an authorized and verified user to change their password. "
                         "The current password must be provided.")
async def change_password(user_data: ChangePasswordRequest,
                          current_user: User = Depends(get_current_verified_user),
                          auth_service: AuthService = Depends(get_auth_service),
                          email_service: EmailService = Depends(get_email_service)):
    # User verification is checked through get_current_verified_user dependency
    if user_data.email != current_user.email:
        raise InvalidEmail

    await auth_service.change_password(user_data.email, user_data.old_password, user_data.new_password)

    # Send notification to user
    await email_service.send_password_change_notification(user_data.email)

    return {"message": "Password changed successfully."}


@router.post("/change-email", response_model=MessageResponse,
             summary="Change email",
             description="Allows an authorized and verified user to change their email.")
async def change_email(user_data: ChangeEmailRequest,
                       current_user: User = Depends(get_current_verified_user),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    # User verification is checked through get_current_verified_user dependency
    if user_data.current_email != current_user.email:
        raise InvalidEmail

    # Сhange email and reset verification status
    await auth_service.change_email(user_data.password, user_data.current_email, user_data.new_email)

    # Send a notify letter to the old email about changing the email
    await email_service.send_email_change_notification(user_data.current_email, user_data.new_email)
    # send a verification letter to the new email
    await email_service.send_email_verification(user_data.new_email)


@router.post("/send-verification-email", response_model=MessageResponse,
             summary="Send email verification",
             description="Sends an email with a verification token to users "
                         "whose accounts are not yet verified.")
async def send_verification_email(email_service: EmailService = Depends(get_email_service),
                                  current_user: User = Depends(get_current_unverified_user)):
    recipient_email = current_user.email
    await email_service.send_email_verification(recipient_email)

    return {"message": "Verification token has been sent to your email."}


@router.get("/verify-email", response_model=MessageResponse,
            summary="Verify email",
            description="Verifies the user's email using the token received by email.")
async def verify_email(email: str = Query(...), token: str = Query(...),
                       auth_service: AuthService = Depends(get_auth_service),
                       email_service: EmailService = Depends(get_email_service)):
    token_is_valid = await email_service.verify_email_verification_token(email, token)
    if not token_is_valid:
        raise VerificationTokenExpired

    await auth_service.verify_user_by_email(email)
    return {"message": "Email successfully verified"}


@router.get("/protected-auth-endpoint", response_model=MessageResponse,
            summary="Access for authorized users",
            description="Endpoint accessible only to authorized users.")
async def protected_auth_endpoint(current_user: User = Depends(get_current_auth_user)):
    return {"message": "You have access to authorized endpoint", "user": current_user}


@router.get("/protected-verify-endpoint", response_model=MessageResponse,
            summary="Access for verified users",
            description="Endpoint accessible only to users with verified email.")
async def protected_verify_endpoint(current_user: User = Depends(get_current_verified_user)):
    return {"message": "You have access to verified endpoint", "user": current_user}
