from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from app.logger import logger

from app.exceptions import CustomException


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except CustomException as http_exc:
            logger.warning(f"HTTPException: {http_exc.detail}")
            return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
        except Exception as exc:
            # Логируем полную трассировку ошибки в консоль
            logger.error("Unhandled exception occurred", exc_info=True)
            raise exc
