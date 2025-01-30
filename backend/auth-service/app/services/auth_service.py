from typing import Optional

from app.models.users import User
from app.repositories.usersRepo import UsersRepository
from app.utils.helpers import generate_hashed_password, check_password


class AuthService:

    def __init__(self, users_repository: UsersRepository):
        self.users_repository: UsersRepository = users_repository

    async def register_user(self, email: str, password: str, fullname: Optional[str]) -> User | None:
        # Проверяем, существует ли пользователь с данным email
        user_is_exist = await self.users_repository.find_by_email(email)
        if user_is_exist:
            return None

        password_info = generate_hashed_password(password)
        user_data = {"email": email,
                     "hashed_password": password_info["hashed_password"],
                     "salt": password_info["salt"],
                     "fullname": fullname}
        new_user = await self.users_repository.create_user(user_data)

        return new_user

    async def login_user(self, email: str, password: str) -> User | None:
        # Проверяем, существует ли пользователь с данным email
        user = await self.users_repository.find_by_email(email)
        if not user:
            return None
        if not check_password(password, user.hashed_password, user.salt):
            return None
        return user
