from typing import Optional

from fastapi import UploadFile

from app.exceptions import TeamNotExist, TeamAlreadyExists
from app.models.teams import Team
from app.repositories.teamsRepo import TeamsRepository

from app.utils.helpers import safe_upload_logo


class TeamService:

    def __init__(self, teams_repository: TeamsRepository):
        self.teams_repository: TeamsRepository = teams_repository

    async def register_team(self, name: str, city: str, logo) -> Team:
        """Создаёт новую команду и загружает логотип (если передан)"""
        team_is_exist = await self.teams_repository.get_by_name(name)
        if team_is_exist:
            raise TeamAlreadyExists

        team_data = {"name": name, "city": city}

        if logo:
            async with safe_upload_logo(name, logo) as logotype:
                team_data["logo_url"] = logotype.logo_url
                return await self.teams_repository.create_team(team_data)

        return await self.teams_repository.create_team(team_data)

    async def update_team(self, team_id: int,
                          name: Optional[str], city: Optional[str],
                          logo: Optional[UploadFile]) -> Team:
        team = await self.get_team_by_id(team_id)
        update_fields = {}

        if name and team.name != name:
            update_fields["name"] = name
        if city and team.city != city:
            update_fields["city"] = city

        if logo:
            async with safe_upload_logo(name or team.name, logo) as logotype:
                update_fields["logo_url"] = logotype.logo_url
                return await self.teams_repository.update_team(team_id, update_fields)

        if not update_fields:
            return team

        return await self.teams_repository.update_team(team_id, update_fields)

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await self.teams_repository.find_by_id(team_id)
        if not team:
            raise TeamNotExist
        return team
