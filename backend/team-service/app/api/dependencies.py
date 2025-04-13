from app.repositories.coachesRepo import CoachesRepository
from app.repositories.playersRepo import PlayersRepository
from app.repositories.teamsRepo import TeamsRepository
from app.services.coach_service import CoachService
from app.services.player_service import PlayerService
from app.services.team_service import TeamService


def get_team_service() -> TeamService:
    return TeamService(TeamsRepository())


def get_player_service() -> PlayerService:
    return PlayerService(PlayersRepository(), TeamsRepository())


def get_coach_service() -> CoachService:
    return CoachService(CoachesRepository(), TeamsRepository())
