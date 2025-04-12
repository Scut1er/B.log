from typing import Optional

from fastapi import Form
from pydantic import BaseModel


class TeamResponse(BaseModel):
    name: str
    city: str
    logo_url: Optional[str]

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
