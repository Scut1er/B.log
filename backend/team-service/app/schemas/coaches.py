from datetime import date, datetime
from typing import Optional

from app.exceptions import InvalidBirthDateFormat
from fastapi import Form
from pydantic import BaseModel, HttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo


class CoachForm(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[date]
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

    @classmethod
    def as_form(
            cls,
            first_name: str = Form(...),
            last_name: str = Form(...),
            birth_date: Optional[str] = Form(None),
            team_id: Optional[int] = Form(None),
    ) -> "CoachForm":
        return cls(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,  # строка — преобразуется валидатором
            team_id=team_id,
        )


class CoachResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    photo_url: Optional[HttpUrl] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
