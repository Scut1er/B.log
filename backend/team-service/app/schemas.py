from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class TeamResponse(BaseModel):
    name: str
    city: str
    logo_url: str | None


class Logo(BaseModel):
    filename: str
    logo_url: str
