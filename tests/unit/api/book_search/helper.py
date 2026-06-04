from datetime import date

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
