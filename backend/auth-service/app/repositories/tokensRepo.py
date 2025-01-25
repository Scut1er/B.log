from datetime import datetime, timezone

from sqlalchemy import select, insert, delete, update

from app.db.db import async_session_maker
from app.models.refresh_tokens import RefreshToken
from app.repositories.repository import SQLAlchemyRepository



class TokensRepository(SQLAlchemyRepository):
    model = RefreshToken

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Сохранение refresh-токена в базе данных.
        Если для пользователя уже существует токен, он перезаписывается."""
        async with async_session_maker() as session:
            async with session.begin():
                # Проверяем, существует ли уже токен для этого пользователя
                existing_token_query = select(RefreshToken).where(RefreshToken.user_id == user_id)
                existing_token = await session.scalar(existing_token_query)
                if existing_token:
                    # Обновляем существующий токен
                    query = update(RefreshToken).where(RefreshToken.user_id == user_id).values(
                        token=token, expires_at=expires_at, created_at=datetime.now(timezone.utc)
                    ).returning(RefreshToken)

                else:
                    # Вставляем новый токен, если его нет
                    query = insert(RefreshToken).values(
                        user_id=user_id, token=token, expires_at=expires_at
                    ).returning(RefreshToken)
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        async with async_session_maker() as session:
            query = select(RefreshToken).where(RefreshToken.token == token)
            result = await session.scalar(query)
            if result:
                return result

    async def is_refresh_token_valid(self, token: str) -> bool:
        """Проверяет, является ли refresh-токен действительным (существует и не истек)"""
        async with async_session_maker() as session:
            query = select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
            result = await session.scalar(query)
            return result is not None

    async def delete_refresh_token(self, token: str) -> None:
        async with async_session_maker() as session:
            query = delete(RefreshToken).where(RefreshToken.token == token)
            await session.execute(query)
            await session.commit()
