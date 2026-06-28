from datetime import date

from bookshelf_app.api.book_search import service as target
from tests.unit.api.book_search.helper import create_book


def test_parse_oreilly_catalog_extracts_table_books():
    html = """
    <table>
      <tr><th>ISBN</th><th>Title</th><th>価格</th><th>発行日</th></tr>
      <tr>
        <td>978-4-8144-0170-3</td>
        <td><a href="/books/9784814401703/">エンジニアリング戦略の作り方</a></td>
        <td>4,180</td>
        <td>2026/05/22</td>
      </tr>
    </table>
    """

    actual = target.parse_oreilly_catalog(html, "https://www.oreilly.co.jp/catalog/")

    assert actual == [
        target.PublisherCatalogBookAppModel(
            isbn13="9784814401703",
            title="エンジニアリング戦略の作り方",
            price="4,180",
            published_at=date(2026, 5, 22),
            source_url="https://www.oreilly.co.jp/books/9784814401703/",
        )
    ]


def test_publisher_catalog_service_returns_latest_enriched_books(monkeypatch):
    google_calls: list[str] = []

    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

        def fetch_books(self):
            return [
                target.PublisherCatalogBookAppModel(
                    isbn13="9784814400003",
                    title="古い本",
                    price=None,
                    published_at=date(2023, 10, 18),
                ),
                target.PublisherCatalogBookAppModel(
                    isbn13="9784814401703",
                    title="新しい本",
                    price=None,
                    published_at=date(2026, 5, 22),
                ),
            ]

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            assert isbn13s == ["9784814401703"]
            return {
                "9784814401703": create_book(
                    source="openbd",
                    isbn13="9784814401703",
                    title="新しい本",
                    publisher="オライリー・ジャパン",
                    published_at=date(2026, 5, 22),
                    image_url="https://example.com/cover.jpg",
                    description="説明",
                )
            }

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            google_calls.append(isbn13)
            return None

    service = target.PublisherCatalogService(FakeGoogle(), FakeOpenBd())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(service, "_load_cache", lambda _key, allow_expired=False: None)
    monkeypatch.setattr(service, "_save_cache", lambda _key, _books: None)
    monkeypatch.setattr(service, "_load_book_metadata_cache", lambda _isbns: {})
    monkeypatch.setattr(service, "_save_book_metadata_cache", lambda _books: None)

    actual = service.search_books("oreilly_japan", limit=1)

    assert [book.isbn13 for book in actual.books] == ["9784814401703"]
    assert actual.books[0].image_url == "https://example.com/cover.jpg"
    assert actual.page == 1
    assert actual.page_size == 1
    assert actual.total_count == 2
    assert google_calls == []


def test_publisher_catalog_service_filters_catalog_books(monkeypatch):
    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            return {}

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            return None

    service = target.PublisherCatalogService(google=FakeGoogle(), openbd=FakeOpenBd())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(
        service,
        "_load_cache",
        lambda _key, allow_expired=False: [
            target.PublisherCatalogBookAppModel(
                isbn13="9784814401703",
                title="エンジニアリング戦略の作り方",
                published_at=date(2026, 5, 22),
            ),
            target.PublisherCatalogBookAppModel(
                isbn13="9784814401642",
                title="入門 Python 3 第3版",
                published_at=date(2026, 6, 16),
            ),
            ],
    )
    monkeypatch.setattr(service, "_load_book_metadata_cache", lambda _isbns: {})
    monkeypatch.setattr(service, "_save_book_metadata_cache", lambda _books: None)

    actual = service.search_books("oreilly_japan", keyword="Python", limit=40)

    assert len(actual.books) == 1
    assert actual.books[0].isbn13 == "9784814401642"
    assert actual.books[0].source == "publisher-catalog"
    assert actual.total_count == 1


def test_publisher_catalog_service_returns_requested_page(monkeypatch):
    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            raise AssertionError("openBD should not be called for cached books")

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            raise AssertionError("Google Books should not be called for cached books")

    catalog_books = [
        target.PublisherCatalogBookAppModel(
            isbn13=f"978481440000{index}",
            title=f"本{index}",
            published_at=date(2026, index, 1),
        )
        for index in range(1, 4)
    ]
    cached_books = {
        book.isbn13: create_book(
            source="openbd",
            isbn13=book.isbn13,
            title=book.title,
            publisher="オライリー・ジャパン",
            published_at=book.published_at,
            image_url=f"https://example.com/{book.isbn13}.jpg",
        )
        for book in catalog_books
    }
    service = target.PublisherCatalogService(google=FakeGoogle(), openbd=FakeOpenBd())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(service, "_load_cache", lambda _key, allow_expired=False: catalog_books)
    monkeypatch.setattr(
        service,
        "_load_book_metadata_cache",
        lambda isbn13s: {isbn13: cached_books[isbn13] for isbn13 in isbn13s},
    )

    actual = service.search_books("oreilly_japan", page=2, limit=1)

    assert [book.isbn13 for book in actual.books] == ["9784814400002"]
    assert actual.page == 2
    assert actual.page_size == 1
    assert actual.total_count == 3


def test_publisher_catalog_service_uses_book_metadata_cache(monkeypatch):
    cached_book = create_book(
        source="openbd",
        isbn13="9784814401703",
        title="キャッシュ済みの本",
        publisher="オライリー・ジャパン",
        published_at=date(2026, 5, 22),
    )

    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            raise AssertionError("openBD should not be called for cached books")

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            raise AssertionError("Google Books should not be called for cached books")

    service = target.PublisherCatalogService(google=FakeGoogle(), openbd=FakeOpenBd())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(
        service,
        "_load_cache",
        lambda _key, allow_expired=False: [
            target.PublisherCatalogBookAppModel(
                isbn13="9784814401703",
                title="エンジニアリング戦略の作り方",
                published_at=date(2026, 5, 22),
            )
        ],
    )
    monkeypatch.setattr(service, "_load_book_metadata_cache", lambda _isbns: {"9784814401703": cached_book})

    actual = service.search_books("oreilly_japan", limit=40)

    assert actual.books == [cached_book]


def test_publisher_catalog_service_supplements_cached_book_without_image(monkeypatch):
    cached_book = create_book(
        source="openbd",
        isbn13="9784814401703",
        title="キャッシュ済みの本",
        publisher="オライリー・ジャパン",
        published_at=date(2026, 5, 22),
        image_url=None,
    )
    google_book = create_book(
        source="google-books",
        isbn13="9784814401703",
        title="Googleの本",
        publisher="オライリー・ジャパン",
        published_at=date(2026, 5, 22),
        image_url="https://example.com/google-cover.jpg",
    )
    saved_books: list[target.BookSearchResultAppModel] = []

    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            assert isbn13s == []
            return {}

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            assert isbn13 == "9784814401703"
            return google_book

    service = target.PublisherCatalogService(google=FakeGoogle(), openbd=FakeOpenBd())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(
        service,
        "_load_cache",
        lambda _key, allow_expired=False: [
            target.PublisherCatalogBookAppModel(
                isbn13="9784814401703",
                title="エンジニアリング戦略の作り方",
                published_at=date(2026, 5, 22),
            )
        ],
    )
    monkeypatch.setattr(service, "_load_book_metadata_cache", lambda _isbns: {"9784814401703": cached_book})
    monkeypatch.setattr(service, "_save_book_metadata_cache", lambda books: saved_books.extend(books))

    actual = service.search_books("oreilly_japan", limit=40)

    assert actual.books[0].image_url == "https://example.com/google-cover.jpg"
    assert saved_books[0].image_url == "https://example.com/google-cover.jpg"
