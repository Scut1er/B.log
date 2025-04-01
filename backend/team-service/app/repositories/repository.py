from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update

from app.db import async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        """Добавление записи"""
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def find_by_id(self, record_id: int):
        """Получение записи по id"""
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == record_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def find_all(self):
        """Получение всех записей"""
        async with async_session_maker() as session:
            stmt = select(self.model)
            result = await session.execute(stmt)
            result = [row[0].to_read_model() for row in result.scalars()]
            return result

    async def update(self, record_id: int, data: dict) -> bool:
        """Обновление 1 записи"""
        async with async_session_maker() as session:
            stmt = (update(self.model).
                    where(self.model.id == record_id).
                    values(**data))
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount  # кол-во измененных строк в бд == True/False
