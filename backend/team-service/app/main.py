import uvicorn
from fastapi import FastAPI

from app.api.router import team_router

app = FastAPI()

app.include_router(team_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
