from app.repositories.teamsRepo import TeamsRepository
from app.services.team_service import TeamService


def get_team_service() -> TeamService:
    return TeamService(TeamsRepository())
