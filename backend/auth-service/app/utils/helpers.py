import bcrypt


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
