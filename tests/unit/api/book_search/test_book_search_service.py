from bookshelf_app.api.book_search import service as target
from tests.unit.api.book_search.helper import create_book


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
