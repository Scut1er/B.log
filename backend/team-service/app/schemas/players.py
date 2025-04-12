from datetime import datetime, date
from typing import Optional

from fastapi import Form, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator, Field
from pydantic_core.core_schema import ValidationInfo

from app.exceptions import InvalidBirthDateFormat, InvalidHeightOrWeight
from app.models.players import PlayerPosition


class PlayerForm(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[date]
    height_cm: Optional[int]
    weight_kg: Optional[int]
    position: Optional[PlayerPosition]
    team_id: Optional[int]

    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birth_date(cls, value: Optional[str], info: ValidationInfo) -> Optional[datetime]:
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidBirthDateFormat

    @field_validator("height_cm", "weight_kg")
    @classmethod
    def validate_positive_range(cls, value: Optional[int], info: ValidationInfo) -> Optional[int]:
        if value is not None and (value <= 0 or value > 300):
            raise InvalidHeightOrWeight
        return value

    @classmethod
    def as_form(
            cls,
            first_name: str = Form(...),
            last_name: str = Form(...),
            birth_date: Optional[str] = Form(None),
            height_cm: Optional[int] = Form(None),
            weight_kg: Optional[int] = Form(None),
            position: Optional[PlayerPosition] = Form(None),
            team_id: Optional[int] = Form(None),
    ) -> "PlayerForm":
        return cls(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,  # строка — преобразуется валидатором
            height_cm=height_cm,
            weight_kg=weight_kg,
            position=position,
            team_id=team_id,
        )


class PlayerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    position: Optional[PlayerPosition] = None
    photo_url: Optional[HttpUrl] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
