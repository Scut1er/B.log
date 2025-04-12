import uvicorn
from fastapi import FastAPI


from app.api.team_router import team_router
from app.api.player_router import player_router

app = FastAPI()

app.include_router(team_router)
app.include_router(player_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
