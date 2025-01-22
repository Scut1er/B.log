from datetime import datetime, timezone, timedelta

from jose import jwt
from app.config import settings


def encode_jwt(payload: dict, private_key: str, algorithm: str = "RS256") -> str:
    """Создание JWT токена с использованием асимметричной криптографии"""
    return jwt.encode(claims=payload, key=private_key, algorithm=algorithm)


def decode_jwt(token: str, public_key: str, algorithm: str = "RS256") -> dict:
    """Декодирование JWT токена с использованием асимметричной криптографии"""
    try:
        return jwt.decode(token=token, key=public_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.JWTError:
        raise Exception("Invalid token")


def create_token(user_id: int,
                 private_key: str,
                 expires_delta: timedelta) -> str:
    payload = {"sub": str(user_id),
               "exp": datetime.now(timezone.utc) + expires_delta}
    return encode_jwt(payload=payload, private_key=private_key)


