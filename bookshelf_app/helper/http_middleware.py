import traceback

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from bookshelf_app.api.shared.errors import (
    ApiException,
    AppValidationError,
    AuthCredentialsError,
    AuthFailedError,
    AuthRolePermissionError,
    DataNotFoundError,
    DomainValidationError,
    DuplicateItemError,
    InvalidAuthError,
)
from bookshelf_app.helper.logger import get_app_logger

logger = get_app_logger(__name__)


class HttpRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response: Response = await call_next(request)
            if response.status_code >= 400:
                logger.error(f"error http status: code:{response.status_code}, {vars(response)}")
        except ApiException as exc:
            logger.exception("ApiException error is happened.")
            response = JSONResponse(
                status_code=exc.status_code,
                content={"message": f"{exc.detail}"},
            )
        except DataNotFoundError as exc:
            logger.exception("DataNotFoundError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": f"{exc}"},
            )
        except DuplicateItemError as exc:
            logger.exception("DuplicateItemError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"message": f"{exc}"},
            )
        except DomainValidationError as exc:
            logger.exception("DomainValidationError error is happened.")
            print(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": f"{exc}"},
            )
        except AppValidationError as exc:
            logger.exception("AppValidationError error is happened.")
            print(traceback.format_exc())
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": f"{exc}"},
            )
        except AuthFailedError:
            logger.exception("AuthFailedError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "failed to auth. UserName(Email) or Password is incorrect."},
            )
        except AuthCredentialsError as exc:
            logger.exception("AuthCredentialsError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": f"{exc}"},
            )
        except InvalidAuthError as exc:
            logger.exception("InvalidAuthError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": f"{exc}"},
            )
        except AuthRolePermissionError as exc:
            logger.exception("AuthRolePermissionError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": f"{exc}"},
            )
        except Exception as exc:
            print(traceback.format_exc())
            logger.exception("Unexpected error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Unexpected error is happened. {exc}"},
            )
        return response
