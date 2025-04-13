from typing import Optional

from app.api.dependencies import get_coach_service
from app.schemas.coaches import CoachForm, CoachResponse
from app.schemas.common import MessageResponse
from app.services.coach_service import CoachService
from fastapi import APIRouter, Depends, File, UploadFile

coach_router = APIRouter(prefix="/coaches", tags=["Coaches"])


@coach_router.post("/create", response_model=CoachResponse)
async def create_coach(
    coach_data: CoachForm = Depends(CoachForm.as_form),
    coach_photo: Optional[UploadFile] = File(
        None, description="Coach photo (optional)"
    ),
    coach_service: CoachService = Depends(get_coach_service),
):
    coach = await coach_service.register_coach(coach_data.dict(), coach_photo)
    return CoachResponse.from_orm(coach)


@coach_router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach_info(
    coach_id: int, coach_service: CoachService = Depends(get_coach_service)
):
    coach = await coach_service.get_coach_by_id(coach_id)
    return CoachResponse.from_orm(coach)


@coach_router.patch("/{coach_id}", response_model=CoachResponse)
async def update_coach_info(
    coach_id: int,
    coach_data: CoachForm = Depends(CoachForm.as_form),
    coach_photo: Optional[UploadFile] = File(
        None, description="Coach photo (optional)"
    ),
    coach_service: CoachService = Depends(get_coach_service),
):
    coach = await coach_service.update_coach(coach_id, coach_data.dict(), coach_photo)
    return CoachResponse.from_orm(coach)


@coach_router.delete("/{coach_id}", response_model=MessageResponse)
async def delete_coach(
    coach_id: int, coach_service: CoachService = Depends(get_coach_service)
):
    await coach_service.delete_coach(coach_id)
    return MessageResponse(message="Successfully deleted")
