from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class Photo(BaseModel):
    filename: str
    image_url: str
