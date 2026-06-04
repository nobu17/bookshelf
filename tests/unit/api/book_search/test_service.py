from datetime import date

import pytest

from bookshelf_app.api.book_search import service as target


def create_book(
    *,
    title: str = "テスト本",
    authors: list[str] | None = None,
    publisher: str = "テスト出版",
    isbn13: str = "9784798121963",
    published_at: date = date(2020, 1, 1),
    image_url: str | None = "https://example.com/cover.jpg",
    description: str | None = "description",
    source: str = "google-books",
) -> target.BookSearchResultAppModel:
    return target.BookSearchResultAppModel(
        source=source,
        source_id=isbn13,
        title=title,
        authors=authors if authors is not None else ["著者"],
        publisher=publisher,
        isbn13=isbn13,
        published_at=published_at,
        image_url=image_url,
        description=description,
    )


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("2020", date(2020, 1, 1), id="year"),
        pytest.param("2020-02", date(2020, 2, 1), id="year month hyphen"),
        pytest.param("2020-02-03", date(2020, 2, 3), id="date hyphen"),
        pytest.param("202002", date(2020, 2, 1), id="year month compact"),
        pytest.param("20200203", date(2020, 2, 3), id="date compact"),
        pytest.param("", date(1970, 1, 1), id="empty"),
        pytest.param(None, date(1970, 1, 1), id="none"),
        pytest.param("unknown", date(1970, 1, 1), id="unknown"),
    ],
)
def test_parse_published_date(value: str | None, expected: date):
    assert target.parse_published_date(value) == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("4798121967", "9784798121963", id="valid isbn10"),
        pytest.param("invalid", None, id="invalid"),
    ],
)
def test_convert_isbn10_to_isbn13(value: str, expected: str | None):
    assert target.convert_isbn10_to_isbn13(value) == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("著者1、著者2/著者3", ["著者1", "著者2", "著者3"], id="separators"),
        pytest.param("", ["著者不明"], id="empty"),
    ],
)
def test_split_authors(value: str, expected: list[str]):
    assert target.split_authors(value) == expected


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


def test_unique_books_prefers_richer_duplicate_isbn():
    poor = create_book(
        isbn13="9784798121963",
        publisher="不明",
        authors=["著者不明"],
        image_url=None,
        description=None,
        published_at=date(1970, 1, 1),
    )
    rich = create_book(
        isbn13="9784798121963",
        publisher="翔泳社",
        authors=["エリックエヴァンス"],
        image_url="https://example.com/cover.jpg",
        description="description",
        published_at=date(2011, 4, 1),
    )

    actual = target.unique_books([poor, rich])

    assert actual == [rich]


def test_unique_books_treats_same_title_publisher_year_as_duplicate():
    pod = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
        description=None,
    )
    sales = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="翔泳社",
        isbn13="9784798131627",
        published_at=date(2015, 12, 1),
        description="richer",
    )

    actual = target.unique_books([pod, sales])

    assert actual == [sales]


def test_unique_books_treats_normalized_title_and_author_as_duplicate():
    rich = create_book(
        title="「実践ドメイン駆動設計」から学ぶDDDの実装入門",
        authors=["WINGSプロジェクト 青木 淳夫"],
        publisher="翔泳社",
        isbn13="9784798161495",
        published_at=date(2019, 5, 31),
        description="richer",
    )
    poor = create_book(
        title="実践ドメイン駆動設計から学ぶDDDの実装入門",
        authors=["青木淳夫"],
        publisher="不明",
        isbn13="9784798161501",
        published_at=date(2019, 5, 31),
        description=None,
    )

    actual = target.unique_books([poor, rich])

    assert actual == [rich]


def test_book_search_service_uses_openbd_fallback_when_google_is_rate_limited():
    class RateLimitedGoogle:
        def find_by_isbn13(self, isbn13: str):
            raise target.BookSearchRateLimitError()

    class FakeOpenBd:
        def find_by_isbn13(self, isbn13: str):
            return create_book(source="openbd", isbn13=isbn13)

    service = target.BookSearchService()
    service._google = RateLimitedGoogle()
    service._openbd = FakeOpenBd()

    actual = service.find_by_isbn13("9784798121963")

    assert actual is not None
    assert actual.source == "openbd"
    assert actual.isbn13 == "9784798121963"
