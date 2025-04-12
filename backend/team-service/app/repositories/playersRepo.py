from sqlalchemy import insert, update

from app.db import async_session_maker
from app.models.players import Player
from app.repositories.repository import SQLAlchemyRepository


class PlayersRepository(SQLAlchemyRepository):
    model = Player

    async def create_player(self, data: dict) -> Player:
        """Создает игрока в БД"""
        async with async_session_maker() as session:
            stmt = insert(Player).values(**data).returning(Player.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_player(self, player_id: int, update_data: dict) -> Player:
        """Обновляет инфо игрока по ID"""
        async with async_session_maker() as session:
            stmt = update(Player).where(Player.id == player_id).values(**update_data
                                                                       ).returning(Player.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_photo_url(self, player_id: int, photo_url: str) -> Player:
        """Обновляет фото игрока"""
        async with (async_session_maker() as session):
            stmt = update(Player).where(Player.id == player_id).values(photo_url=photo_url
                                                                       ).returning(Player.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()
