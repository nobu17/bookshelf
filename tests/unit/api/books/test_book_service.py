import uuid
from datetime import date

import pytest

from bookshelf_app.api.books.domain import Author, Authors, Book, BookImageUrl, BookTitle, ISBN13, Publisher, Tags
from bookshelf_app.api.books.service import BookService, BookUpdateAppModel
from bookshelf_app.api.shared.errors import DataNotFoundError


def create_book(
    book_id: uuid.UUID | None = None,
    isbn13: str = "9784814400690",
    title: str = "入門 継続的デリバリー",
    publisher: str = "オライリージャパン",
    authors: list[str] | None = None,
    published_at: date = date(2023, 1, 10),
    image_url: str = "",
) -> Book:
    book = Book(
        ISBN13(isbn13),
        BookTitle(title),
        Publisher(publisher),
        Authors([Author(author) for author in (authors or ["著者1", "著者2"])]),
        published_at,
        Tags([]),
        BookImageUrl(image_url),
    )
    if book_id is not None:
        book.book_id = book_id
    return book


def test_book_update_uses_book_id_and_does_not_apply_create_duplicate_rule():
    target_id = uuid.uuid4()
    other_id = uuid.uuid4()
    target = create_book(
        book_id=target_id,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        authors=["著者A"],
        published_at=date(2024, 1, 10),
    )
    other = create_book(book_id=other_id)
    book_repos = FakeBookRepository([target, other])
    service = BookService(book_repos, FakeTagRepository())

    actual = service.update(
        BookUpdateAppModel(
            book_id=target_id,
            isbn13=other.isbn13.value,
            title="別レコードだが同じISBN年",
            publisher=other.publisher.get_value(),
            authors=[author.get_value() for author in other.authors.get_values()],
            published_at=other.published_at,
            image_url="https://example.com/updated.jpg",
        )
    )

    assert actual.book_id == target_id
    assert actual.book_id != other_id
    assert actual.isbn13 == other.isbn13.value
    assert actual.title == "別レコードだが同じISBN年"
    assert actual.image_url == "https://example.com/updated.jpg"
    assert book_repos.updated.book_id == target_id


def test_book_update_not_found():
    service = BookService(FakeBookRepository([]), FakeTagRepository())

    with pytest.raises(DataNotFoundError):
        service.update(
            BookUpdateAppModel(
                book_id=uuid.uuid4(),
                isbn13="9784814400690",
                title="入門 継続的デリバリー",
                publisher="オライリージャパン",
                authors=["著者1"],
                published_at=date(2023, 1, 10),
            )
        )


class FakeBookRepository:
    def __init__(self, books: list[Book]):
        self.books = {book.book_id: book for book in books}
        self.updated: Book | None = None

    def find_by_isbn13(self, isbn13: ISBN13) -> list[Book]:
        return [book for book in self.books.values() if book.isbn13 == isbn13]

    def find_by_id(self, id: uuid.UUID) -> Book | None:
        return self.books.get(id)

    def create(self, item: Book) -> Book:
        self.books[item.book_id] = item
        return item

    def update(self, item: Book) -> Book:
        self.updated = item
        self.books[item.book_id] = item
        return item

    def update_tags(self, id: uuid.UUID, tag_ids: list[uuid.UUID]) -> None:
        return

    def delete(self, id: uuid.UUID) -> None:
        return


class FakeTagRepository:
    def list(self):
        return []

    def find_by_ids(self, ids):
        return []
