from fastapi import FastAPI

from app.api.router import team_router

app = FastAPI()

app.include_router(team_router)