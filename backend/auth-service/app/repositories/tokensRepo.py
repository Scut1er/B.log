from datetime import datetime, timezone

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from app.db.db import async_session_maker
from app.models.refresh_tokens import RefreshToken
from app.repositories.repository import SQLAlchemyRepository


class TokensRepository(SQLAlchemyRepository):
    model = RefreshToken

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Saves RefreshToken in the database.
        If a token already exists for the user, it is rewritten."""
        async with async_session_maker() as session:
            async with session.begin():
                query = insert(RefreshToken).values(
                    user_id=user_id, token=token, expires_at=expires_at
                ).on_conflict_do_update(  # If the user has a token, we replace it with a new
                    index_elements=[RefreshToken.user_id],
                    set_={
                        "token": token,
                        "expires_at": expires_at,
                        "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
                    }
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

    async def get_refresh_token_by_user_id(self, user_id: int) -> RefreshToken | None:
        async with async_session_maker() as session:
            query = select(RefreshToken).where(RefreshToken.user_id == user_id)
            result = await session.scalar(query)
            if result:
                return result

    async def is_refresh_token_valid(self, token: str) -> bool:
        """Проверяет, является ли refresh-токен действительным (существует и не истек)"""
        async with async_session_maker() as session:
            query = select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
            )
            result = await session.scalar(query)
            return result is not None

    async def delete_refresh_token(self, token: str) -> None:
        async with async_session_maker() as session:
            query = delete(RefreshToken).where(RefreshToken.token == token)
            await session.execute(query)
            await session.commit()
