from typing import Optional

from fastapi import APIRouter, UploadFile, Depends, Form, File

from app.api.dependencies import get_team_service
from app.schemas import TeamResponse
from app.services.team_service import TeamService

team_router = APIRouter(prefix="/team")


@team_router.post("/create", response_model=TeamResponse)
async def create_team(name: str = Form(...), city: str = Form(...),
                      logo: Optional[UploadFile] = File(None, description="Team logo (optional)"),
                      team_service: TeamService = Depends(get_team_service)):
    team = await team_service.register_team(name, city, logo)
    return TeamResponse(name=team.name, city=team.city, logo_url=team.logo_url)


@team_router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, team_service: TeamService = Depends(get_team_service)):
    team = await team_service.get_team_by_id(team_id)
    return TeamResponse(name=team.name, city=team.city, logo_url=team.logo_url)


@team_router.put("/{team_id}")
async def update_team(team_id: int):
    ...
