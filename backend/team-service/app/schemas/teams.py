from typing import List, Optional

from app.schemas.coaches import CoachResponse
from app.schemas.players import PlayerResponse
from fastapi import Form
from pydantic import BaseModel


class TeamResponse(BaseModel):
    id: int
    name: str
    city: str
    logo_url: Optional[str]
    players: List[PlayerResponse] = []
    coach: Optional[CoachResponse] = None

    class Config:
        from_attributes = True


class TeamForm(BaseModel):
    name: Optional[str]
    city: Optional[str]

    @classmethod
    def as_form(
            cls,
            name: Optional[str] = Form(None),
            city: Optional[str] = Form(None),
    ) -> "TeamForm":
        return cls(name=name, city=city)
