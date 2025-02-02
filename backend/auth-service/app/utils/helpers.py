import uuid

import bcrypt
from fastapi import Response

from app.config import settings


def create_email_verification_token() -> str:
    """Генерирует уникальный токен для верификации email."""
    return str(uuid.uuid4())


def set_token_cookie(response: Response, token_type: str, token: str) -> None:
    """Устанавливает токен в куки."""
    key = "access_token"
    max_age = int(settings.ACCESS_TOKEN_EXPIRE_TIME_MINUTES) * 60
    if token_type == "refresh":
        key = "refresh_token"
        max_age = int(settings.REFRESH_TOKEN_EXPIRE_TIME_MINUTES) * 60
    cookie_params = {
        "httponly": True,
        "secure": True,
        "samesite": "strict",
        "max_age": max_age,
    }
    response.set_cookie(key=key, value=token, **cookie_params)


def generate_hashed_password(password) -> dict:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return {"hashed_password": hashed_password, "salt": salt.decode('utf-8')}


def check_password(entered_password: str, stored_hashed_password: str, stored_salt: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с сохраненным хэшом и солью."""
    # Преобразуем соль обратно в байты
    salt = stored_salt.encode('utf-8')
    # Хэшируем введенный пароль с использованием сохраненной соли
    hashed_entered_password = bcrypt.hashpw(entered_password.encode('utf-8'), salt).decode('utf-8')
    # Сравниваем хэши
    return hashed_entered_password == stored_hashed_password
