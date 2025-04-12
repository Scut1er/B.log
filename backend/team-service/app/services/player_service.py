from typing import Optional

from fastapi import UploadFile

from app.exceptions import UpdateLogoError, UpdatePhotoError, TeamNotExist
from app.minio_db import delete_file
from app.models.players import Player
from app.repositories.playersRepo import PlayersRepository
from app.repositories.teamsRepo import TeamsRepository
from app.utils.helpers import upload_image_minio


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
