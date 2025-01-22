from app.models.users import Users
from app.repositories.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = Users