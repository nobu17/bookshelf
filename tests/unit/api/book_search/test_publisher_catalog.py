from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

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


def test_parse_gihyo_catalog_response_extracts_books():
    data = {
        "list": {
            "978-4-297-15790-6": {
                "series": "",
                "title": "システム開発と<wbr>「具体と抽象」",
                "subtitle": "〜問題発見と問題解決を往復する<wbr>「思考のメタ化」<wbr>を身につける&#8288;〜",
                "price": [2000, 0],
                "release": ["2026.7.28", ""],
                "url": "/book/2026/978-4-297-15790-6",
            },
            "invalid": {
                "title": "ISBNなし",
                "release": ["2026.7.28", ""],
            },
        }
    }

    actual = target.parse_gihyo_catalog_response(data, "https://gihyo.jp")

    assert actual == [
        target.PublisherCatalogBookAppModel(
            isbn13="9784297157906",
            title="システム開発と「具体と抽象」 〜問題発見と問題解決を往復する「思考のメタ化」を身につける⁠〜",
            price="2,000",
            published_at=date(2026, 7, 28),
            source_url="https://gihyo.jp/book/2026/978-4-297-15790-6",
        )
    ]


def test_fetch_gihyo_catalog_books_reads_all_pages(monkeypatch):
    calls: list[dict[str, str]] = []

    def fake_fetch_json(_url: str, params: dict[str, str]):
        calls.append(params)
        if params["offset"] == "0":
            return {
                "list": {
                    "978-4-297-15790-6": {
                        "title": "1冊目",
                        "release": ["2026.7.28", ""],
                        "url": "/book/2026/978-4-297-15790-6",
                    }
                },
                "next": True,
            }
        return {
            "list": {
                "978-4-297-15727-2": {
                    "title": "2冊目",
                    "release": ["2026.7.27", ""],
                    "url": "/book/2026/978-4-297-15727-2",
                }
            },
            "next": False,
        }

    monkeypatch.setattr(target, "fetch_json", fake_fetch_json)

    actual = target.fetch_gihyo_catalog_books(
        "https://gihyo.jp/api_gh/book/genre/test",
        "https://gihyo.jp",
        100,
    )

    assert [book.isbn13 for book in actual] == ["9784297157906", "9784297157272"]
    assert calls == [
        {"limit": "100", "offset": "0"},
        {"limit": "100", "offset": "100"},
    ]


def test_gihyo_catalog_provider_merges_genres_by_newest(monkeypatch):
    def fake_fetch_gihyo_catalog_books(url: str, _base_url: str, _limit: int):
        if "first" in url:
            return [
                target.PublisherCatalogBookAppModel(
                    isbn13="9784297150001",
                    title="古いプログラミング本",
                    published_at=date(2024, 1, 1),
                )
            ]
        return [
            target.PublisherCatalogBookAppModel(
                isbn13="9784297150002",
                title="新しいネットワーク本",
                published_at=date(2026, 1, 1),
            )
        ]

    monkeypatch.setattr(target, "fetch_gihyo_catalog_books", fake_fetch_gihyo_catalog_books)
    provider = target.GihyoCatalogProvider()
    provider.catalog_urls = ["first", "second"]

    actual = provider.fetch_books()

    assert [book.isbn13 for book in actual] == ["9784297150002", "9784297150001"]


def test_publisher_catalog_service_lists_supported_publishers():
    service = target.PublisherCatalogService(google=object(), openbd=object())

    actual = service.list_publishers()

    assert actual == [
        target.PublisherAppModel("oreilly_japan", "オライリー・ジャパン"),
        target.PublisherAppModel("gihyo", "技術評論社"),
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


def test_forced_metadata_refresh_preserves_cached_image_and_description(monkeypatch):
    cached_book = create_book(
        source="google-books",
        isbn13="9784814401703",
        image_url="https://example.com/cached-cover.jpg",
        description="既存の説明",
    )
    openbd_book = create_book(
        source="openbd",
        isbn13="9784814401703",
        image_url=None,
        description=None,
    )
    saved_books: list[target.BookSearchResultAppModel] = []

    class FakeOpenBd:
        def find_by_isbn13s(self, isbn13s: list[str]):
            return {"9784814401703": openbd_book}

    class FakeGoogle:
        def find_by_isbn13(self, isbn13: str):
            return None

    service = target.PublisherCatalogService(google=FakeGoogle(), openbd=FakeOpenBd())
    monkeypatch.setattr(
        service,
        "_load_book_metadata_cache",
        lambda _isbn13s, allow_expired=False: {"9784814401703": cached_book},
    )
    monkeypatch.setattr(service, "_save_book_metadata_cache", lambda books: saved_books.extend(books))

    actual = service._enrich_books(
        [
            target.PublisherCatalogBookAppModel(
                isbn13="9784814401703",
                title="テスト本",
                published_at=date(2026, 1, 1),
            )
        ],
        "オライリー・ジャパン",
        force_refresh=True,
    )

    assert actual[0].image_url == "https://example.com/cached-cover.jpg"
    assert actual[0].description == "既存の説明"
    assert saved_books == actual


def test_metadata_cache_needs_refresh_checks_age_and_image():
    refresh_before = datetime.now(timezone.utc) - timedelta(days=14)
    complete_book = create_book(image_url="https://example.com/cover.jpg")
    incomplete_book = create_book(image_url=None)

    fresh = SimpleNamespace(
        fetched_at=refresh_before + timedelta(days=1),
        payload_json=target.book_search_result_to_json(complete_book),
        is_deleted=False,
    )
    stale = SimpleNamespace(
        fetched_at=refresh_before - timedelta(seconds=1),
        payload_json=target.book_search_result_to_json(complete_book),
        is_deleted=False,
    )
    missing_image = SimpleNamespace(
        fetched_at=refresh_before + timedelta(days=1),
        payload_json=target.book_search_result_to_json(incomplete_book),
        is_deleted=False,
    )

    assert not target.metadata_cache_needs_refresh(fresh, refresh_before)
    assert target.metadata_cache_needs_refresh(stale, refresh_before)
    assert target.metadata_cache_needs_refresh(missing_image, refresh_before)
    assert target.metadata_cache_needs_refresh(None, refresh_before)


def test_publisher_catalog_service_warms_candidates_in_batches(monkeypatch):
    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    catalog_books = [
        target.PublisherCatalogBookAppModel(
            isbn13=f"978481440000{index}",
            title=f"本{index}",
            published_at=date(2026, index, 1),
        )
        for index in range(1, 4)
    ]
    batches: list[list[str]] = []
    service = target.PublisherCatalogService(google=object(), openbd=object())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(service, "_get_catalog_books", lambda _provider: catalog_books)
    monkeypatch.setattr(
        service,
        "_find_metadata_refresh_candidates",
        lambda _books, _refresh_before: catalog_books,
    )

    def fake_enrich(books, _publisher_name, force_refresh=False, google_delay_seconds=0):
        assert force_refresh
        assert google_delay_seconds == 0
        batches.append([book.isbn13 for book in books])
        return [create_book(isbn13=book.isbn13) for book in books]

    monkeypatch.setattr(service, "_enrich_books", fake_enrich)

    actual = service.warm_metadata_cache(
        "oreilly_japan",
        refresh_after_days=14,
        batch_size=2,
        google_delay_seconds=0,
        batch_delay_seconds=0,
    )

    assert batches == [["9784814400001", "9784814400002"], ["9784814400003"]]
    assert actual == target.MetadataCacheWarmupResult(
        catalog_count=3,
        candidate_count=3,
        refreshed_count=3,
        failed_count=0,
    )


def test_publisher_catalog_service_continues_after_failed_batch(monkeypatch):
    class FakeProvider:
        publisher_id = "oreilly_japan"
        publisher_name = "オライリー・ジャパン"
        cache_key = "oreilly_japan_catalog"

    catalog_books = [
        target.PublisherCatalogBookAppModel(
            isbn13=f"978481440000{index}",
            title=f"本{index}",
            published_at=date(2026, index, 1),
        )
        for index in range(1, 3)
    ]
    service = target.PublisherCatalogService(google=object(), openbd=object())
    service._providers = {"oreilly_japan": FakeProvider()}
    monkeypatch.setattr(service, "_get_catalog_books", lambda _provider: catalog_books)
    monkeypatch.setattr(
        service,
        "_find_metadata_refresh_candidates",
        lambda _books, _refresh_before: catalog_books,
    )
    calls = 0

    def fake_enrich(books, _publisher_name, force_refresh=False, google_delay_seconds=0):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("temporary failure")
        return [create_book(isbn13=books[0].isbn13)]

    monkeypatch.setattr(service, "_enrich_books", fake_enrich)

    actual = service.warm_metadata_cache(
        "oreilly_japan",
        refresh_after_days=14,
        batch_size=1,
        google_delay_seconds=0,
        batch_delay_seconds=0,
    )

    assert actual.refreshed_count == 1
    assert actual.failed_count == 1
