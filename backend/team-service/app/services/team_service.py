from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile

from app.exceptions import TeamNotExist, TeamAlreadyExists, UpdateLogoError
from app.minio_db import delete_file
from app.models.teams import Team
from app.repositories.teamsRepo import TeamsRepository

from app.utils.helpers import upload_logo


class TeamService:

    def __init__(self, teams_repository: TeamsRepository):
        self.teams_repository: TeamsRepository = teams_repository

    async def register_team(self, name: str, city: str, logo: Optional[UploadFile]) -> Team:
        """Создаёт новую команду и загружает логотип (если передан)"""
        team_is_exist = await self.teams_repository.get_by_name(name)
        if team_is_exist:
            raise TeamAlreadyExists

        team_data = {"name": name, "city": city}
        team = await self.teams_repository.create_team(team_data)

        if logo:
            logotype = await upload_logo(logo)  # Загружаем логотип
            team = await self.teams_repository.update_logo_url(team.id, logotype.logo_url)
            if not team:
                delete_file("team-logos", logotype.filename)  # Если обновление не удалось, удаляем
                raise UpdateLogoError

        return team

    async def update_team(self, team_id: int,
                          name: Optional[str], city: Optional[str],
                          logo: Optional[UploadFile]) -> Team:
        team = await self.get_team_by_id(team_id)
        update_fields = {}

        if name and team.name != name:
            existing_team = await self.teams_repository.get_by_name(name)
            if existing_team:
                raise TeamAlreadyExists
            update_fields["name"] = name
        if city and team.city != city:
            update_fields["city"] = city
        if update_fields:
            team = await self.teams_repository.update_team(team_id, update_fields)

        if logo:
            old_logo_filename = None
            if team.logo_url:  # Проверяем, есть ли старый логотип
                old_logo_filename = urlparse(str(team.logo_url)).path.split("/")[-1]

            logotype = await upload_logo(logo)  # Загружаем новый логотип
            team = await self.teams_repository.update_logo_url(team.id, logotype.logo_url)
            if not team:
                delete_file("team-logos", logotype.filename)  # Если обновление не удалось, удаляем новый логотип
                raise UpdateLogoError
            else:
                if old_logo_filename:
                    delete_file("team-logos", old_logo_filename)  # Если обновление удалось, удаляем старый логотип

        return team

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await self.teams_repository.find_by_id(team_id)
        if not team:
            raise TeamNotExist
        return team
