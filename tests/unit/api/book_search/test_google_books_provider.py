from datetime import date

from bookshelf_app.api.book_search import service as target


def test_create_google_search_queries_adds_field_specific_queries():
    actual = target.create_google_search_queries("オライリー")

    assert actual == [
        "オライリー",
        "intitle:オライリー",
        "inpublisher:オライリー",
    ]


def test_create_google_search_queries_keeps_isbn_search_single_query():
    actual = target.create_google_search_queries("978-4-7981-2196-3")

    assert actual == ["isbn:9784798121963"]


def test_google_books_provider_search_uses_publisher_query(monkeypatch):
    queries: list[str] = []

    def fake_fetch_json(_url: str, params: dict[str, str]):
        assert params["orderBy"] == "newest"
        queries.append(params["q"])
        if params["q"] == "inpublisher:オライリー":
            return {
                "items": [
                    {
                        "id": "google-id",
                        "volumeInfo": {
                            "title": "Publisher matched book",
                            "authors": ["著者"],
                            "publisher": "オライリー・ジャパン",
                            "publishedDate": "2024-01",
                            "industryIdentifiers": [{"type": "ISBN_13", "identifier": "9784814400737"}],
                        },
                    }
                ]
            }
        return {"items": []}

    monkeypatch.setattr(target, "fetch_json", fake_fetch_json)

    actual = target.GoogleBooksProvider(api_key="dummy").search("オライリー")

    assert queries == [
        "オライリー",
        "intitle:オライリー",
        "inpublisher:オライリー",
    ]
    assert len(actual) == 1
    assert actual[0].publisher == "オライリー・ジャパン"


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


def test_convert_google_volume_converts_image_url_to_https():
    actual = target.convert_google_volume(
        {
            "id": "google-id",
            "volumeInfo": {
                "title": "HTTPS cover book",
                "authors": ["著者"],
                "publisher": "出版社",
                "publishedDate": "2011-04",
                "industryIdentifiers": [{"type": "ISBN_13", "identifier": "9784798121963"}],
                "imageLinks": {
                    "thumbnail": "http://books.google.com/books/content?id=abc&printsec=frontcover"
                },
            },
        }
    )

    assert actual is not None
    assert actual.image_url == "https://books.google.com/books/content?id=abc&printsec=frontcover"


def test_convert_google_volume_normalizes_description_html():
    actual = target.convert_google_volume(
        {
            "id": "google-id",
            "volumeInfo": {
                "title": "Description book",
                "authors": ["著者"],
                "publisher": "出版社",
                "publishedDate": "2011-04",
                "industryIdentifiers": [{"type": "ISBN_13", "identifier": "9784798121963"}],
                "description": "概要<br><b>太字</b>",
            },
        }
    )

    assert actual is not None
    assert actual.description == "概要\n太字"


def test_extract_openbd_description_prefers_description_text_content():
    actual = target.extract_openbd_description(
        {
            "onix": {
                "CollateralDetail": {
                    "TextContent": [
                        {"TextTypeCode": "04", "Text": "目次"},
                        {"TextTypeCode": "03", "Text": "紹介文<br>本文"},
                    ]
                }
            }
        }
    )

    assert actual == "紹介文\n本文"
