from typing import Optional

from fastapi import HTTPException, status


class CustomException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(status_code=self.status_code,
                         detail=detail if detail is not None else self.detail)


class UserNotVerified(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is not verified. You can verify email at /send-verification-email."


class UserAlreadyVerified(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is already verified."


class UserNotExist(CustomException):
    status_code = status.HTTP_404_NOT_FOUND


class RegistrationFailed(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Registration failed"


class TokenMissing(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED


class TokenInvalid(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is invalid"


class TokenVerificationFailed(TokenInvalid):
    detail = "The process of verification of tokens was failed"


class TokenExpired(TokenInvalid):
    detail = "Token is expired"


class RefreshTokenInvalid(TokenInvalid):
    detail = "Refresh token is invalid or expired"


class VerificationTokenExpired(TokenInvalid):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "The verification token has expired. Request a new verification email."


class EmailVerificationFailed(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email verification failed"


class InvalidCredentials(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"


class ForbiddenAccess(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access to this resource is forbidden"


class InternalServerError(CustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An internal server error occurred"


class UserAlreadyExists(CustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"


class InvalidEmail(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email is incorrect"


class EmailIsTaken(CustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email is already taken"
