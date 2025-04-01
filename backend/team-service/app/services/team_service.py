from app.exceptions import TeamNotExist, TeamAlreadyExists
from app.minio_db import delete_file
from app.models.teams import Team
from app.repositories.teamsRepo import TeamsRepository


from app.utils.helpers import upload_logo


class TeamService:

    def __init__(self, teams_repository: TeamsRepository):
        self.teams_repository: TeamsRepository = teams_repository

    async def register_team(self, name: str, city: str, logo) -> Team:
        team_is_exist = await self.teams_repository.get_by_name(name)
        if team_is_exist:
            raise TeamAlreadyExists
        logo_url = None
        if logo:
            logotype = await upload_logo(name, logo)
            logo_url = logotype.logo_url
        team_data = {"name": name, "city": city, "logo_url": logo_url}
        team = await self.teams_repository.create_team(team_data)
        return team

    async def update_logo_team(self, team_id: int, name: str, logo) -> Team:
        logotype = await upload_logo(name, logo)

        # Обновляем URL логотипа в БД
        try:
            team = await self.teams_repository.update_logo_url(team_id, logotype.logo_url)
            return team
        except Exception as e:
            # Если БД обновить не удалось — удаляем загруженный файл
            delete_file("team-logos", logotype.filename)
            raise e

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await self.teams_repository.find_by_id(team_id)
        return team if team else TeamNotExist
