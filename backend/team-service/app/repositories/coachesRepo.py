from app.db import async_session_maker
from app.models.coaches import Coach
from app.repositories.repository import SQLAlchemyRepository
from sqlalchemy import insert, update


class CoachesRepository(SQLAlchemyRepository):
    model = Coach

    async def create_coach(self, data: dict) -> Coach:
        """Создает тренера в БД"""
        async with async_session_maker() as session:
            stmt = insert(Coach).values(**data).returning(Coach.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_coach(self, coach_id: int, update_data: dict) -> Coach:
        """Обновляет инфо тренера по ID"""
        async with async_session_maker() as session:
            stmt = (
                update(Coach)
                .where(Coach.id == coach_id)
                .values(**update_data)
                .returning(Coach.__table__.columns)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_photo_url(self, coach_id: int, photo_url: str) -> Coach:
        """Обновляет фото тренера"""
        async with async_session_maker() as session:
            stmt = (
                update(Coach)
                .where(Coach.id == coach_id)
                .values(photo_url=photo_url)
                .returning(Coach.__table__.columns)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()
