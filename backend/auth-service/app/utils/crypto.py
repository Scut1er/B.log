from datetime import datetime

from jose import jwt

from app.config import settings


def decode_access_jwt(token: str) -> dict:
    try:
        return jwt.decode(token=token, key=settings.ACCESS_PUBLIC_KEY, algorithms=["ES256"])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.JWTError:
        raise Exception("Invalid token")


def decode_refresh_jwt(token: str) -> dict:
    try:
        return jwt.decode(token=token, key=settings.REFRESH_PUBLIC_KEY, algorithms=["ES256"])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.JWTError:
        raise Exception("Invalid token")


def create_jwt_token(user_id: int,
                     token_type: str,
                     private_key: str,
                     expires_at: datetime) -> str:
    payload = {"user_id": str(user_id),
               "type": token_type,
               "exp": expires_at}
    return jwt.encode(claims=payload, key=private_key, algorithm="ES256")
