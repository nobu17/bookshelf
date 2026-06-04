from datetime import date

from bookshelf_app.api.book_search import service as target


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
