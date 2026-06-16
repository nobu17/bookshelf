import asyncio
from types import SimpleNamespace

from fastapi import Response
from sqlalchemy.exc import OperationalError

from bookshelf_app.helper import http_middleware


def test_is_transient_db_error_detects_azure_sql_40613():
    exc = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("Database is not currently available. Error code 40613."),
    )

    assert http_middleware.is_transient_db_error(exc)


def test_is_transient_db_error_ignores_regular_exception():
    assert not http_middleware.is_transient_db_error(ValueError("40613 as plain validation message"))


def test_call_next_with_transient_retry_retries_safe_method(monkeypatch):
    monkeypatch.setattr(http_middleware, "TRANSIENT_RETRY_DELAYS_SECONDS", (0.0,))
    request = SimpleNamespace(method="GET", url=SimpleNamespace(path="/api/book_with_reviews/latest/100"))
    calls = 0
    transient_error = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("Database is not currently available. Error code 40613."),
    )

    async def call_next(_request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise transient_error
        return Response(status_code=200)

    response = asyncio.run(http_middleware._call_next_with_transient_retry(request, call_next))

    assert response.status_code == 200
    assert calls == 2


def test_call_next_with_transient_retry_does_not_retry_mutating_method(monkeypatch):
    monkeypatch.setattr(http_middleware, "TRANSIENT_RETRY_DELAYS_SECONDS", (0.0,))
    request = SimpleNamespace(method="POST", url=SimpleNamespace(path="/api/reviews"))
    calls = 0
    transient_error = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("Database is not currently available. Error code 40613."),
    )

    async def call_next(_request):
        nonlocal calls
        calls += 1
        raise transient_error

    try:
        asyncio.run(http_middleware._call_next_with_transient_retry(request, call_next))
    except OperationalError:
        pass

    assert calls == 1
