from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from bookshelf_app.helper.logger import get_app_logger

logger = get_app_logger(__name__)


def handle_custom_error(app: FastAPI) -> FastAPI:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        logger.error(exc)
        return JSONResponse(content={"message": f"Invalid request:{exc.body}"}, status_code=422)
    
    return app
