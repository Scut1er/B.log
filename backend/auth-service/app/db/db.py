from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


from app.config import settings

DB_URL = settings.DATABASE_URL
DATABASE_PARAMS = {}

engine = create_async_engine(DB_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    ...
