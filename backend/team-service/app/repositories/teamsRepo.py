from sqlalchemy import select, update, insert

from app.db import async_session_maker
from app.models.teams import Team
from app.repositories.repository import SQLAlchemyRepository


class TeamsRepository(SQLAlchemyRepository):
    model = Team

    async def create_team(self, data: dict) -> Team:
        """Создает команду в БД"""
        async with async_session_maker() as session:
            stmt = insert(Team).values(**data).returning(Team.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def update_logo_url(self, team_id: int, logo_url: str) -> Team:
        """Обновляет логотип у команды"""
        async with async_session_maker() as session:
            stmt = update(Team).where(Team.id == team_id).values(logo_url=logo_url).returning(Team.__table__.columns)
            result = await session.execute(stmt)
            await session.commit()
            return result.fetchone()

    async def get_by_name(self, team_name: str) -> Team:
        async with async_session_maker() as session:
            stmt = select(Team).where(Team.name == team_name)
            result = await session.execute(stmt)
            team = result.fetchone()
            return team if team else None
