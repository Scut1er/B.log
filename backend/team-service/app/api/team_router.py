from typing import Optional

from app.api.dependencies import get_team_service
from app.schemas.common import MessageResponse
from app.schemas.teams import TeamForm, TeamResponse
from app.services.team_service import TeamService
from fastapi import APIRouter, Depends, File, UploadFile

team_router = APIRouter(prefix="/teams", tags=["Teams"])


@team_router.post("/create", response_model=TeamResponse)
async def create_team(
    team_data: TeamForm = Depends(TeamForm.as_form),
    logo: Optional[UploadFile] = File(None, description="Team logo (optional)"),
    team_service: TeamService = Depends(get_team_service),
):
    team = await team_service.register_team(team_data.dict(), logo)
    return TeamResponse.from_orm(team)


@team_router.get("/{team_id}", response_model=TeamResponse)
async def get_team_info(
    team_id: int, team_service: TeamService = Depends(get_team_service)
):
    team = await team_service.get_team_by_id(team_id)
    return TeamResponse.from_orm(team)


@team_router.patch("/{team_id}", response_model=TeamResponse)
async def update_team_info(
    team_id: int,
    team_data: TeamForm = Depends(TeamForm.as_form),
    logo: Optional[UploadFile] = File(None, description="Team logo (optional)"),
    team_service: TeamService = Depends(get_team_service),
):
    team = await team_service.update_team(team_id, team_data.dict(), logo)
    return TeamResponse.from_orm(team)


@team_router.delete("/{team_id}", response_model=MessageResponse)
async def delete_team(
    team_id: int, team_service: TeamService = Depends(get_team_service)
):
    await team_service.delete_team(team_id)
    return MessageResponse(message="Successfully deleted")
