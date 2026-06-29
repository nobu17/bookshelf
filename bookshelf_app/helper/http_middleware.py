import asyncio
from time import perf_counter
import traceback

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, OperationalError
from starlette.middleware.base import BaseHTTPMiddleware

from bookshelf_app.api.shared.errors import (
    ApiException,
    AppValidationError,
    AuthCredentialsError,
    AuthFailedError,
    UserNotFoundError,
    AuthRolePermissionError,
    DataNotFoundError,
    DomainValidationError,
    DuplicateItemError,
    InvalidAuthError,
)
from bookshelf_app.helper.logger import get_app_logger

logger = get_app_logger(__name__)

TRANSIENT_DB_ERROR_CODES = {
    20047,
    40197,
    40501,
    40613,
    49918,
    49919,
    49920,
}
TRANSIENT_RETRY_METHODS = {"GET", "HEAD", "OPTIONS"}
TRANSIENT_RETRY_DELAYS_SECONDS = (1.0, 3.0, 7.0, 12.0)


class HttpRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response: Response = await _call_next_with_transient_retry(request, call_next)
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
        except UserNotFoundError:
            logger.exception("UserNotFoundError error is happened.")
            response = JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "failed to find user. incorrect user_id."},
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


async def _call_next_with_transient_retry(request: Request, call_next) -> Response:
    if request.method not in TRANSIENT_RETRY_METHODS:
        return await call_next(request)

    retry_count = len(TRANSIENT_RETRY_DELAYS_SECONDS)
    request_started_at = perf_counter()
    for attempt in range(retry_count + 1):
        attempt_started_at = perf_counter()
        try:
            response = await call_next(request)
            if attempt > 0:
                logger.info(
                    "Request recovered after transient database error. "
                    f"method:{request.method}, path:{request.url.path}, "
                    f"retries:{attempt}, total_elapsed:{perf_counter() - request_started_at:.3f}"
                )
            return response
        except Exception as exc:
            if attempt >= retry_count or not is_transient_db_error(exc):
                raise

            delay = TRANSIENT_RETRY_DELAYS_SECONDS[attempt]
            error_codes = find_transient_db_error_codes(exc)
            logger.warning(
                "Transient database error is happened. retrying request. "
                f"method:{request.method}, path:{request.url.path}, "
                f"attempt:{attempt + 1}/{retry_count}, delay:{delay}, "
                f"error_codes:{error_codes or ['unknown']}, "
                f"attempt_elapsed:{perf_counter() - attempt_started_at:.3f}, "
                f"total_elapsed:{perf_counter() - request_started_at:.3f}"
            )
            await asyncio.sleep(delay)

    return await call_next(request)


def is_transient_db_error(exc: Exception) -> bool:
    if not isinstance(exc, (DBAPIError, OperationalError)) and not _contains_dbapi_error(exc):
        return False

    return bool(find_transient_db_error_codes(exc))


def find_transient_db_error_codes(exc: BaseException) -> list[int]:
    exception_text = _flatten_exception_text(exc)
    return sorted(code for code in TRANSIENT_DB_ERROR_CODES if str(code) in exception_text)


def _contains_dbapi_error(exc: BaseException) -> bool:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, DBAPIError):
            return True
        current = current.__cause__ or current.__context__

    return False


def _flatten_exception_text(exc: BaseException) -> str:
    texts: list[str] = []
    current: BaseException | None = exc
    while current is not None:
        texts.append(str(current))
        texts.extend(str(arg) for arg in getattr(current, "args", ()))
        current = current.__cause__ or current.__context__

    return " ".join(texts)
