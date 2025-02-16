from datetime import datetime

from jose import jwt

from app.config import settings
from app.exceptions import TokenInvalid, TokenExpired


def decode_jwt(token: str, key: str) -> dict:
    try:
        return jwt.decode(token=token, key=key, algorithms=["ES256"])
    except jwt.ExpiredSignatureError:
        raise TokenExpired
    except jwt.JWTError:
        raise TokenInvalid


def create_jwt_token(user_id: int,
                     token_type: str,
                     private_key: str,
                     expires_at: datetime) -> str:
    payload = {"user_id": str(user_id),
               "type": token_type,
               "exp": expires_at}
    return jwt.encode(claims=payload, key=private_key, algorithm="ES256")
