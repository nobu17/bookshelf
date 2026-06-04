import pytest

from bookshelf_app.api.book_search import service as target


@pytest.mark.parametrize(
    ["data"],
    [
        pytest.param([], id="empty response"),
        pytest.param([None], id="null item"),
        pytest.param([{}], id="missing summary"),
    ],
)
def test_openbd_provider_returns_none_when_summary_is_missing(monkeypatch, data: list):
    monkeypatch.setattr(target, "fetch_json", lambda url, params: data)

    actual = target.OpenBdProvider().find_by_isbn13("9784798121963")

    assert actual is None


def test_openbd_provider_converts_cover_url_to_https(monkeypatch):
    monkeypatch.setattr(
        target,
        "fetch_json",
        lambda url, params: [
            {
                "summary": {
                    "isbn": "9784798121963",
                    "title": "openBD title",
                    "author": "著者1、著者2",
                    "publisher": "出版社",
                    "pubdate": "20110401",
                    "cover": "http://example.com/cover.jpg",
                }
            }
        ],
    )

    actual = target.OpenBdProvider().find_by_isbn13("9784798121963")

    assert actual is not None
    assert actual.image_url == "https://example.com/cover.jpg"
    assert actual.authors == ["著者1", "著者2"]
