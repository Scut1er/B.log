from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends

from app.api.dependencies import get_player_service
from app.schemas.players import PlayerForm, PlayerResponse
from app.services.player_service import PlayerService

player_router = APIRouter(prefix="/players")


@player_router.post("/create", response_model=PlayerResponse)
async def create_player(player_data: PlayerForm = Depends(PlayerForm.as_form),
                        player_photo: Optional[UploadFile] = File(None, description="Player photo (optional)"),
                        player_service: PlayerService = Depends(get_player_service)):
    player = await player_service.register_player(player_data.dict(), player_photo)
    return PlayerResponse.from_orm(player)

