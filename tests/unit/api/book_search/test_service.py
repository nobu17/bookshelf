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


def test_convert_google_volume_uses_isbn10_when_isbn13_is_missing():
    actual = target.convert_google_volume(
        {
            "id": "google-id",
            "volumeInfo": {
                "title": "ISBN10 book",
                "authors": ["著者"],
                "publisher": "出版社",
                "publishedDate": "2011-04",
                "industryIdentifiers": [{"type": "ISBN_10", "identifier": "4798121967"}],
            },
        }
    )

    assert actual is not None
    assert actual.isbn13 == "9784798121963"
    assert actual.published_at == date(2011, 4, 1)


def test_convert_google_volume_ignores_item_without_isbn():
    actual = target.convert_google_volume({"volumeInfo": {"title": "No ISBN"}})

    assert actual is None


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


def test_unique_books_keeps_same_title_publisher_when_year_is_different():
    first = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
    )
    second = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="翔泳社",
        isbn13="9784798131627",
        published_at=date(2016, 3, 1),
    )

    actual = target.unique_books([first, second])

    assert actual == [first, second]


def test_unique_books_keeps_same_title_year_when_publisher_is_different():
    first = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
    )
    second = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="別出版社",
        isbn13="9784798131627",
        published_at=date(2015, 3, 1),
    )

    actual = target.unique_books([first, second])

    assert actual == [first, second]


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


def test_book_search_service_returns_empty_for_blank_keyword():
    service = target.BookSearchService.__new__(target.BookSearchService)

    actual = service.search("   ")

    assert actual == []


def test_book_search_service_uses_google_for_keyword_search():
    book = create_book()

    class FakeGoogle:
        def search(self, keyword: str):
            assert keyword == "ドメイン駆動設計"
            return [book]

    service = target.BookSearchService.__new__(target.BookSearchService)
    service._google = FakeGoogle()

    actual = service.search(" ドメイン駆動設計 ")

    assert actual == [book]


def test_book_search_service_merges_google_and_openbd_for_isbn_search():
    google = create_book(title="Google title", image_url="https://google.example.com/cover.jpg")
    openbd = create_book(source="openbd", title="openBD title", image_url=None)

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            return google

    class FakeOpenBd:
        def find_by_isbn13(self, isbn13: str):
            return openbd

    service = target.BookSearchService.__new__(target.BookSearchService)
    service._google = FakeGoogle()
    service._openbd = FakeOpenBd()

    actual = service.search("9784798121963")

    assert actual == [target.merge_book_search_result(google, openbd)]


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


def test_book_search_service_returns_empty_when_google_rate_limited_and_openbd_has_no_result():
    class RateLimitedGoogle:
        def find_by_isbn13(self, isbn13: str):
            raise target.BookSearchRateLimitError()

    class EmptyOpenBd:
        def find_by_isbn13(self, isbn13: str):
            return None

    service = target.BookSearchService.__new__(target.BookSearchService)
    service._google = RateLimitedGoogle()
    service._openbd = EmptyOpenBd()

    actual = service.search("9784798121963")

    assert actual == []
