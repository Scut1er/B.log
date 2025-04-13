from typing import Optional
from urllib.parse import urlparse

from app.exceptions import (DeletePlayerError, PlayerNotExist, TeamNotExist,
                            UpdatePhotoError)
from app.minio_db import delete_file
from app.models.players import Player
from app.repositories.playersRepo import PlayersRepository
from app.repositories.teamsRepo import TeamsRepository
from app.utils.helpers import upload_image_minio
from fastapi import UploadFile


class PlayerService:

    def __init__(self, players_repository: PlayersRepository,
                 teams_repository: TeamsRepository):
        self.players_repository: PlayersRepository = players_repository
        self.teams_repository: TeamsRepository = teams_repository

    async def register_player(self, player_data: dict, player_photo: Optional[UploadFile]) -> Player:
        """Создаёт нового игрока и загружает его фото (если передано)"""
        #  Проверка существования команды, если указан team_id
        team_id = player_data.get("team_id")
        if team_id is not None:
            team = await self.teams_repository.find_by_id(team_id)
            if team is None:
                raise TeamNotExist

        player = await self.players_repository.create_player(player_data)

        if player_photo:
            player_photo_obj = await upload_image_minio(player_photo, "player-photos")  # Загружаем фото игрока
            player = await self.players_repository.update_photo_url(player.id, player_photo_obj.image_url)
            if not player:
                delete_file("player-photos", player_photo_obj.filename)  # Если обновление не удалось, удаляем
                raise UpdatePhotoError

        return player

    async def update_player(self, player_id: int, player_data: dict, photo: Optional[UploadFile]) -> Player:
        player = await self.get_player_by_id(player_id)
        update_fields = {}

        # Проверка team_id отдельно
        team_id = player_data.get("team_id")
        if team_id is not None and team_id != player.team_id:
            team = await self.teams_repository.find_by_id(team_id)
            if team is None:
                raise TeamNotExist
            update_fields["team_id"] = team_id

        # Обновляем стандартные поля, если они изменились
        for field in ("first_name", "last_name", "birth_date", "height_cm", "weight_kg", "position"):
            new_value = player_data.get(field)
            if new_value is not None and getattr(player, field) != new_value:
                update_fields[field] = new_value

        # Применяем изменения
        if update_fields:
            player = await self.players_repository.update_player(player_id, update_fields)

        # Обновление фото, если передано новое
        if photo:
            player = await self._replace_photo(player, photo)

        return player

    async def _replace_photo(self, player: Player, photo: UploadFile) -> Player:
        old_filename = None
        if player.photo_url:  # Проверяем, есть ли старое фото
            old_filename = player.photo_url.split("/")[-1]

        # Загружаем новое
        photo_obj = await upload_image_minio(photo, "player-photos")
        updated_player = await self.players_repository.update_photo_url(player.id, photo_obj.image_url)

        if not updated_player:
            delete_file("player-photos", photo_obj.filename)
            raise UpdatePhotoError

        if old_filename:
            delete_file("player-photos", old_filename)

        return updated_player

    async def get_player_by_id(self, player_id: int) -> Player:
        player = await self.players_repository.find_by_id(player_id)
        if not player:
            raise PlayerNotExist
        return player

    async def delete_player(self, player_id: int):
        player = await self.get_player_by_id(player_id)

        # Удаляем фото, если он есть
        if player.photo_url:
            photo_filename = urlparse(str(player.photo_url)).path.split("/")[-1]
            delete_file("player-photos", photo_filename)

        player_is_deleted = await self.players_repository.delete_by_id(player_id)
        if not player_is_deleted:
            raise DeletePlayerError
