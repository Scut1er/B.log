from datetime import datetime

from jose import jwt

from app.exceptions import TokenInvalid, TokenExpired


def decode_jwt(token: str, key: str) -> dict:
    try:
        return jwt.decode(token=token, key=key, algorithms=["ES256"])
    except jwt.ExpiredSignatureError:
        raise TokenExpired
    except jwt.JWTError:
        raise TokenInvalid


def decode_token_with_public_keys(token: str, keys: list) -> dict:
    """Декодирует токен с использованием списка публичных ключей."""
    for public_key in keys:
        if public_key:
            try:
                decoded_token = decode_jwt(token, public_key)
                return decoded_token
            except Exception:
                continue
    raise TokenInvalid


def create_jwt_token(user_id: int,
                     token_type: str,
                     private_key: str,
                     expires_at: datetime) -> str:
    payload = {"user_id": str(user_id),
               "type": token_type,
               "exp": expires_at}
    return jwt.encode(claims=payload, key=private_key, algorithm="ES256")
