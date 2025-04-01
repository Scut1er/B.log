from app.models.players import Player
from app.repositories.repository import SQLAlchemyRepository


class PlayersRepository(SQLAlchemyRepository):
    model = Player
