from app.db import async_session_maker
from app.models.teams import Team
from app.repositories.repository import SQLAlchemyRepository
from sqlalchemy import insert, select, update
from sqlalchemy.orm import joinedload


class TeamsRepository(SQLAlchemyRepository):
    model = Team

    async def create_team(self, data: dict) -> Team:
        """Создает команду в БД"""
        async with async_session_maker() as session:
            stmt = insert(Team).values(**data).returning(Team.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_team(self, team_id: int, update_data: dict) -> Team:
        """Обновляет инфо команды по ID и возвращает с игроками и тренером"""
        async with async_session_maker() as session:
            stmt = update(Team).where(Team.id == team_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()
            return await self._get_with_relations(session, team_id)

    async def update_logo_url(self, team_id: int, logo_url: str) -> Team:
        """Обновляет логотип у команды и возвращает с игроками и тренером"""
        async with async_session_maker() as session:
            stmt = update(Team).where(Team.id == team_id).values(logo_url=logo_url)
            await session.execute(stmt)
            await session.commit()
            return await self._get_with_relations(session, team_id)

    async def get_by_name(self, team_name: str) -> Team:
        async with async_session_maker() as session:
            stmt = select(Team).where(Team.name == team_name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_with_players_and_coach(self, team_id: int) -> Team:
        """Возвращает команду с её игроками и тренером"""
        async with async_session_maker() as session:
            return await self._get_with_relations(session, team_id)

    async def _get_with_relations(self, session, team_id: int) -> Team:
        """Приватный метод: возвращает команду с отношениями"""
        stmt = (
            select(Team)
            .options(joinedload(Team.players), joinedload(Team.coach))
            .where(Team.id == team_id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
