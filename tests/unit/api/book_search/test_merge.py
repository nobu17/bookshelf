from datetime import date

from bookshelf_app.api.book_search import service as target
from tests.unit.api.book_search.helper import create_book


def test_merge_book_search_result_prefers_valid_openbd_fields_and_google_image_fallback():
    google = create_book(
        title="Google title",
        authors=["Google author"],
        publisher="Google publisher",
        isbn13="9784798121963",
        published_at=date(2011, 4, 1),
        image_url="https://google.example.com/cover.jpg",
        description="google description",
    )
    openbd = create_book(
        source="openbd",
        title="openBD title",
        authors=["openBD author"],
        publisher="openBD publisher",
        isbn13="9784798121963",
        published_at=date(2011, 4, 2),
        image_url=None,
        description=None,
    )

    actual = target.merge_book_search_result(google, openbd)

    assert actual.source == "openbd"
    assert actual.title == "openBD title"
    assert actual.authors == ["openBD author"]
    assert actual.publisher == "openBD publisher"
    assert actual.published_at == date(2011, 4, 2)
    assert actual.image_url == "https://google.example.com/cover.jpg"
    assert actual.description == "google description"


def test_merge_book_search_result_uses_google_when_openbd_fields_are_unknown():
    google = create_book(
        title="Google title",
        authors=["Google author"],
        publisher="Google publisher",
        published_at=date(2011, 4, 1),
    )
    openbd = create_book(
        source="openbd",
        title="タイトル不明",
        authors=["著者不明"],
        publisher="不明",
        published_at=date(1970, 1, 1),
        image_url="https://openbd.example.com/cover.jpg",
    )

    actual = target.merge_book_search_result(google, openbd)

    assert actual.title == "Google title"
    assert actual.authors == ["Google author"]
    assert actual.publisher == "Google publisher"
    assert actual.published_at == date(2011, 4, 1)
    assert actual.image_url == "https://openbd.example.com/cover.jpg"
