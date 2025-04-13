from typing import Optional
from urllib.parse import urlparse

from app.exceptions import (CoachNotExist, DeleteCoachError, TeamNotExist,
                            UpdatePhotoError)
from app.minio_db import delete_file
from app.models.coaches import Coach
from app.repositories.coachesRepo import CoachesRepository
from app.repositories.teamsRepo import TeamsRepository
from app.utils.helpers import upload_image_minio
from fastapi import UploadFile


class CoachService:

    def __init__(self, coaches_repository: CoachesRepository,
                 teams_repository: TeamsRepository):
        self.coaches_repository: CoachesRepository = coaches_repository
        self.teams_repository: TeamsRepository = teams_repository

    async def register_coach(self, coach_data: dict, coach_photo: Optional[UploadFile]) -> Coach:
        """Создаёт нового тренера и загружает его фото (если передано)"""
        #  Проверка существования команды, если указан team_id
        team_id = coach_data.get("team_id")
        if team_id is not None:
            team = await self.teams_repository.find_by_id(team_id)
            if team is None:
                raise TeamNotExist

        coach = await self.coaches_repository.create_coach(coach_data)

        if coach_photo:
            coach_photo_obj = await upload_image_minio(coach_photo, "coach-photos")  # Загружаем фото тренера
            coach = await self.coaches_repository.update_photo_url(coach.id, coach_photo_obj.image_url)
            if not coach:
                delete_file("coach-photos", coach_photo_obj.filename)  # Если обновление не удалось, удаляем
                raise UpdatePhotoError

        return coach

    async def update_coach(self, coach_id: int, coach_data: dict, photo: Optional[UploadFile]) -> Coach:
        coach = await self.get_coach_by_id(coach_id)
        update_fields = {}

        # Проверка team_id отдельно
        team_id = coach_data.get("team_id")
        if team_id is not None and team_id != coach.team_id:
            team = await self.teams_repository.find_by_id(team_id)
            if team is None:
                raise TeamNotExist
            update_fields["team_id"] = team_id

        # Обновляем стандартные поля, если они изменились
        for field in ("first_name", "last_name", "birth_date"):
            new_value = coach_data.get(field)
            if new_value is not None and getattr(coach, field) != new_value:
                update_fields[field] = new_value

        # Применяем изменения
        if update_fields:
            coach = await self.coaches_repository.update_coach(coach_id, update_fields)

        # Обновление фото, если передано новое
        if photo:
            coach = await self._replace_photo(coach, photo)

        return coach

    async def _replace_photo(self, coach: Coach, photo: UploadFile) -> Coach:
        old_filename = None
        if coach.photo_url:  # Проверяем, есть ли старое фото
            old_filename = coach.photo_url.split("/")[-1]

        # Загружаем новое
        photo_obj = await upload_image_minio(photo, "coach-photos")
        updated_coach = await self.coaches_repository.update_photo_url(coach.id, photo_obj.image_url)

        if not updated_coach:
            delete_file("coach-photos", photo_obj.filename)
            raise UpdatePhotoError

        if old_filename:
            delete_file("coach-photos", old_filename)

        return updated_coach

    async def get_coach_by_id(self, coach_id: int) -> Coach:
        coach = await self.coaches_repository.find_by_id(coach_id)
        if not coach:
            raise CoachNotExist
        return coach

    async def delete_coach(self, coach_id: int):
        coach = await self.get_coach_by_id(coach_id)

        # Удаляем фото, если он есть
        if coach.photo_url:
            photo_filename = urlparse(str(coach.photo_url)).path.split("/")[-1]
            delete_file("coach-photos", photo_filename)

        coach_is_deleted = await self.coaches_repository.delete_by_id(coach_id)
        if not coach_is_deleted:
            raise DeleteCoachError
