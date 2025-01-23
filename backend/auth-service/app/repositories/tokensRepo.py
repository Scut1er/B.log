from datetime import datetime, timezone

from sqlalchemy import select, insert, delete, update

from app.db.db import async_session_maker
from app.models.refresh_tokens import RefreshTokens
from app.repositories.repository import SQLAlchemyRepository
from app.schemas import RefreshTokenSchema


class TokensRepository(SQLAlchemyRepository):
    model = RefreshTokens

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime):
        """Сохранение refresh-токена в базе данных.
        Если для пользователя уже существует токен, он перезаписывается."""
        async with async_session_maker() as session:
            async with session.begin():
                # Проверяем, существует ли уже токен для этого пользователя
                existing_token_query = select(RefreshTokens).where(RefreshTokens.user_id == user_id)
                existing_token = await session.scalar(existing_token_query)
                if existing_token:
                    # Обновляем существующий токен
                    update_query = update(RefreshTokens).where(RefreshTokens.user_id == user_id).values(
                        token=token, expires_at=expires_at
                    )
                    await session.execute(update_query)
                else:
                    # Вставляем новый токен, если его нет
                    insert_query = insert(RefreshTokens).values(
                        user_id=user_id, token=token, expires_at=expires_at
                    )
                    await session.execute(insert_query)
                await session.commit()

    async def get_refresh_token(self, token: str) -> RefreshTokenSchema | None:
        async with async_session_maker() as session:
            query = select(RefreshTokens).where(RefreshTokens.token == token)
            result = await session.scalar(query)
            if result:
                return RefreshTokenSchema.from_orm(result)

    async def is_refresh_token_valid(self, token: str) -> bool:
        """Проверяет, является ли refresh-токен действительным (существует и не истек)"""
        async with async_session_maker() as session:
            query = select(RefreshTokens).where(
                RefreshTokens.token == token,
                RefreshTokens.expires_at > datetime.now(timezone.utc)
            )
            result = await session.scalar(query)
            return result is not None

    async def delete_refresh_token(self, token: str) -> None:
        async with async_session_maker() as session:
            query = delete(RefreshTokens).where(RefreshTokens.token == token)
            await session.execute(query)
            await session.commit()
