import uvicorn
from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(title="Auth")
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)