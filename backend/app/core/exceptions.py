from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class AppException(Exception):
    """Custom Base Exception cho ứng dụng"""
    def __init__(self, status_code: int, message: str, details: any = None):
        self.status_code = status_code
        self.message = message
        self.details = details

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "details": exc.details},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"message": "Validation Error", "details": exc.errors()},
        )
