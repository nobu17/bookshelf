from datetime import date

from bookshelf_app.api.book_search.service import BookSearchRateLimitError, BookSearchResultAppModel
import bookshelf_app.api.book_search.router as target_router

URL_BASE = "/api/book_search"


def test_book_search_returns_books_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            assert keyword == "ドメイン駆動設計"
            return [
                BookSearchResultAppModel(
                    source="google-books",
                    source_id="google-book-id",
                    title="ドメイン駆動設計入門",
                    authors=["著者1"],
                    publisher="テスト出版",
                    isbn13="9784798121963",
                    published_at=date(2020, 2, 3),
                    image_url="https://example.com/cover.jpg",
                    description="テスト説明",
                )
            ]

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "ドメイン駆動設計"})

    assert response.status_code == 200
    body = response.json()
    assert body["books"] == [
        {
            "source": "google-books",
            "source_id": "google-book-id",
            "title": "ドメイン駆動設計入門",
            "authors": ["著者1"],
            "publisher": "テスト出版",
            "isbn13": "9784798121963",
            "published_at": "2020-02-03",
            "image_url": "https://example.com/cover.jpg",
            "description": "テスト説明",
        }
    ]


def test_book_search_returns_multiple_books_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            assert keyword == "設計"
            return [
                BookSearchResultAppModel(
                    source="google-books",
                    source_id="google-book-id-1",
                    title="設計入門",
                    authors=["著者1"],
                    publisher="テスト出版",
                    isbn13="9784798121963",
                    published_at=date(2020, 2, 3),
                    image_url="https://example.com/cover1.jpg",
                    description="説明1",
                ),
                BookSearchResultAppModel(
                    source="openbd",
                    source_id="9784814400737",
                    title="設計実践",
                    authors=["著者2"],
                    publisher="別出版",
                    isbn13="9784814400737",
                    published_at=date(2024, 7, 20),
                    image_url=None,
                    description=None,
                ),
            ]

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "設計"})

    assert response.status_code == 200
    assert [book["source_id"] for book in response.json()["books"]] == ["google-book-id-1", "9784814400737"]


def test_book_search_returns_nullable_fields_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            return [
                BookSearchResultAppModel(
                    source="openbd",
                    source_id="9784798121963",
                    title="ドメイン駆動設計入門",
                    authors=["著者1"],
                    publisher="テスト出版",
                    isbn13="9784798121963",
                    published_at=date(2020, 2, 3),
                    image_url=None,
                    description=None,
                )
            ]

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "9784798121963"})

    assert response.status_code == 200
    book = response.json()["books"][0]
    assert book["image_url"] is None
    assert book["description"] is None


def test_book_search_returns_empty_books_for_blank_keyword_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            assert keyword == "   "
            return []

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "   "})

    assert response.status_code == 200
    assert response.json() == {"books": []}


def test_book_search_requires_keyword(integration_client):
    response = integration_client.get(URL_BASE)

    assert response.status_code == 422


def test_book_search_returns_rate_limit_message_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            raise BookSearchRateLimitError()

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "ドメイン駆動設計"})

    assert response.status_code == 429
    assert response.json()["detail"] == "外部書籍検索APIの利用制限に達しました。しばらく時間を置いてから再度お試しください。"


def test_book_search_unexpected_error_is_internal_server_error_without_external_api(integration_client, monkeypatch):
    class FakeBookSearchService:
        def search(self, keyword: str):
            raise RuntimeError("unexpected provider error")

    monkeypatch.setattr(target_router, "BookSearchService", FakeBookSearchService)

    response = integration_client.get(URL_BASE, params={"keyword": "ドメイン駆動設計"})

    assert response.status_code == 500
