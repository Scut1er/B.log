from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete

from app.db import async_session_maker
from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)  # SQLAlchemy модель


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository, Generic[ModelType]):
    model: Type[ModelType]

    async def add_one(self, data: dict) -> int:
        """Добавление записи c возвратом id"""
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

    async def delete_by_id(self, record_id: int) -> bool:
        """Удаление записи по id"""
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == record_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0  # Кол-во удалённых строк

    async def find_all(self) -> list[ModelType]:
        """Получение всех записей"""
        async with async_session_maker() as session:
            stmt = select(self.model)
            result = await session.execute(stmt)
            result = [row[0].to_read_model() for row in result.scalars()]
            return result

    async def update_returning_bool(self, record_id: int, data: dict) -> bool:
        """Обновление 1 записи с возвратом успеха"""
        async with async_session_maker() as session:
            stmt = (update(self.model).
                    where(self.model.id == record_id).
                    values(**data))
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount  # кол-во измененных строк в бд == True/False
