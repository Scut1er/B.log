from datetime import datetime

from jose import jwt

from app.config import settings


def decode_jwt(token: str, public_key: str, algorithm: str) -> dict:
    """Декодирование JWT токена с использованием асимметричной криптографии"""
    try:
        return jwt.decode(token=token, key=public_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.JWTError:
        raise Exception("Invalid token")


def create_jwt_token(user_id: int,
                     token_type: str,
                     private_key: str,
                     expires_at: datetime) -> str:
    payload = {"sub": str(user_id),
               "type": token_type,
               "exp": expires_at}
    return jwt.encode(claims=payload, key=private_key, algorithm="ES256")


