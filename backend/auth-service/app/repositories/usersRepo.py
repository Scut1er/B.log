from sqlalchemy import select, insert, update

from app.db.db import async_session_maker
from app.models.users import User
from app.repositories.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User

    async def create_user(self, data: dict) -> User:
        """Добавление пользователя"""
        async with async_session_maker() as session:
            stmt = insert(User).values(**data).returning(User.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def find_by_email(self, email: str) -> User | None:
        """Получение записи по email"""
        async with async_session_maker() as session:
            stmt = select(User).where(User.email == email)
            result = await session.scalar(stmt)
            if result:
                return result

    async def update_password(self, email: str, hashed_password: str, salt: str) -> bool:
        async with async_session_maker() as session:
            stmt = update(User).where(User.email == email).values(hashed_password=hashed_password, salt=salt)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def update_email(self, old_email: str, new_email: str) -> bool:
        async with async_session_maker() as session:
            stmt = update(User).where(User.email == old_email).values(email=new_email)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def update_verification_status(self, email: str, status: bool) -> bool:
        async with async_session_maker() as session:
            stmt = update(User).where(User.email == email).values(is_verified=status)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
