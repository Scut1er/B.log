import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.auth import oauth_router as oauth_router
from app.logger import logger
from middlewares.exception_middleware import ExceptionMiddleware

app = FastAPI(title="Auth")


# Обработчик для всех необработанных исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


app.include_router(auth_router)
app.add_middleware(SessionMiddleware, secret_key="adsasdasasd")
app.include_router(oauth_router)
# заменил ExceptionMiddleware на general_exception_handler (логированием занимается FastAPI)
"""app.add_middleware(ExceptionMiddleware)"""

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
