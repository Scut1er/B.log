from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile

from app.exceptions import TeamNotExist, TeamAlreadyExists, UpdateLogoError, DeleteTeamError
from app.minio_db import delete_file
from app.models.teams import Team
from app.repositories.teamsRepo import TeamsRepository

from app.utils.helpers import upload_image_minio


class TeamService:

    def __init__(self, teams_repository: TeamsRepository):
        self.teams_repository: TeamsRepository = teams_repository

    async def register_team(self, team_data: dict, logo: Optional[UploadFile]) -> Team:
        """Создаёт новую команду и загружает логотип (если передан)"""
        team_is_exist = await self.teams_repository.get_by_name(team_data["name"])
        if team_is_exist:
            raise TeamAlreadyExists

        team = await self.teams_repository.create_team(team_data)

        if logo:
            logotype_obj = await upload_image_minio(logo, "team-logos")  # Загружаем логотип
            team = await self.teams_repository.update_logo_url(team.id, logotype_obj.image_url)
            if not team:
                delete_file("team-logos", logotype_obj.filename)  # Если обновление не удалось, удаляем
                raise UpdateLogoError

        return team

    async def update_team(self, team_id: int,
                          team_data: dict,
                          logo: Optional[UploadFile]) -> Team:
        name = team_data.get("name")
        city = team_data.get("city")

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
            team = await self._replace_logo(team, logo)

        return team

    async def _replace_logo(self, team: Team, new_logo: UploadFile) -> Team:
        old_logo_filename = None
        if team.logo_url:  # Проверяем, есть ли старый логотип
            old_logo_filename = urlparse(str(team.logo_url)).path.split("/")[-1]

        logotype_obj = await upload_image_minio(new_logo, "team-logos")  # Загружаем новый логотип
        updated_team = await self.teams_repository.update_logo_url(team.id, logotype_obj.image_url)

        if not updated_team:
            delete_file("team-logos", logotype_obj.filename)  # Если обновление не удалось, удаляем новый логотип
            raise UpdateLogoError

        if old_logo_filename:
            delete_file("team-logos", old_logo_filename)  # Если обновление удалось, удаляем старый логотип

        return updated_team

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await self.teams_repository.find_by_id(team_id)
        if not team:
            raise TeamNotExist
        return team

    async def delete_team(self, team_id: int):
        team = await self.get_team_by_id(team_id)

        # Удаляем логотип, если он есть
        if team.logo_url:
            logo_filename = urlparse(str(team.logo_url)).path.split("/")[-1]
            delete_file("team-logos", logo_filename)

        team_is_deleted = await self.teams_repository.delete_by_id(team_id)
        if not team_is_deleted:
            raise DeleteTeamError
