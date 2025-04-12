from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends

from app.api.dependencies import get_player_service
from app.schemas.common import MessageResponse
from app.schemas.players import PlayerForm, PlayerResponse
from app.services.player_service import PlayerService

player_router = APIRouter(prefix="/players", tags=["Players"])


@player_router.post("/create", response_model=PlayerResponse)
async def create_player(player_data: PlayerForm = Depends(PlayerForm.as_form),
                        player_photo: Optional[UploadFile] = File(None, description="Player photo (optional)"),
                        player_service: PlayerService = Depends(get_player_service)):
    player = await player_service.register_player(player_data.dict(), player_photo)
    return PlayerResponse.from_orm(player)


@player_router.get("/{player_id}", response_model=PlayerResponse)
async def get_player_info(player_id: int, player_service: PlayerService = Depends(get_player_service)):
    player = await player_service.get_player_by_id(player_id)
    return PlayerResponse.from_orm(player)


@player_router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player_info(
        player_id: int,
        player_data: PlayerForm = Depends(PlayerForm.as_form),
        player_photo: Optional[UploadFile] = File(None, description="Player photo (optional)"),
        player_service: PlayerService = Depends(get_player_service),
):
    player = await player_service.update_player(player_id, player_data.dict(), player_photo)
    return PlayerResponse.from_orm(player)


@player_router.delete("/{player_id}", response_model=MessageResponse)
async def delete_player(player_id: int, player_service: PlayerService = Depends(get_player_service)):
    await player_service.delete_player(player_id)
    return MessageResponse(message="Successfully deleted")
