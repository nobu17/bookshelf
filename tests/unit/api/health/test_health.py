import asyncio

from bookshelf_app.api.health.router import health


def test_health_returns_ok():
    response = asyncio.run(health())

    assert response.status == "ok"
