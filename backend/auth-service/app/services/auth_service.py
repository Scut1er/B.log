from typing import Optional

from app.exceptions import UserAlreadyExists, InvalidCredentials, EmailIsTaken, EmailVerificationFailed, \
    UserAlreadyVerified, NotFoundEmailOAuth
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
            raise UserAlreadyExists

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

    async def login_or_register_oauth_user(self, provider: str, userinfo: dict) -> User:
        provider_mapping = {
            "google": {"email": "email", "fullname": "name", "provider_id": "sub"},
            "yandex": {"email": "default_email", "fullname": "real_name", "provider_id": "id"},
        }

        mapping = provider_mapping.get(provider)
        if not mapping:
            raise ValueError(f"OAuth провайдер {provider} не поддерживается")

        email = userinfo.get(mapping["email"])
        fullname = userinfo.get(mapping["fullname"], email.split("@")[0] if email else "Unknown")
        provider_id = userinfo.get(mapping["provider_id"])

        if not email:
            raise NotFoundEmailOAuth

        existing_user = await self.users_repository.find_by_email(email)

        if not existing_user:
            user = await self.users_repository.create_oauth_user(
                email=email,
                fullname=fullname,
                provider=provider,
                provider_id=provider_id,
            )
            return user
        return existing_user

    async def verify_user_by_email(self, email: str) -> bool:
        user = await self.users_repository.find_by_email(email)
        if not user:
            raise EmailVerificationFailed(detail="User not found. Try /send-verification-email again")
        if user.is_verified:
            raise UserAlreadyVerified

        user_is_updated = await self.users_repository.update_verification_status(email, True)
        if not user_is_updated:
            raise EmailVerificationFailed
        return user_is_updated

    async def change_password(self, email: str, current_password: str, new_password: str) -> bool:
        user = await self.login_user(email, current_password)  # Check the old password
        if not user:
            raise InvalidCredentials

        password_info = generate_hashed_password(new_password)
        hashed_password = password_info["hashed_password"]
        salt = password_info["salt"]
        return await self.users_repository.update_password(email, hashed_password, salt)

    async def change_email(self, password: str, current_email: str, new_email: str) -> bool:
        # Проверка не занят ли новый email другим пользователем
        email_is_taken = await self.users_repository.find_by_email(new_email)
        if email_is_taken:
            raise EmailIsTaken

        # Проверка данных входа
        user = await self.login_user(current_email, password)
        if not user:
            raise InvalidCredentials

        # Изменение email пользователя и обнуление его верификации
        await self.users_repository.update_email(current_email, new_email)
        return await self.users_repository.update_verification_status(new_email, False)
