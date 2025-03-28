import uuid
from dataclasses import dataclass
from datetime import date

from bookshelf_app.api.books.domain import ISBN13, Book, BookFactory, IBookRepository
from bookshelf_app.api.shared.errors import DataNotFoundError
from bookshelf_app.api.tags.domain import ITagRepository
from bookshelf_app.api.tags.service import TagAppModel


@dataclass(frozen=False)
class BookAppModel:
    book_id: uuid.UUID
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date
    tags: list[TagAppModel]

    def __init__(self, book_domain: Book):
        self.book_id = book_domain.book_id
        self.isbn13 = book_domain.isbn13.value
        self.title = book_domain.title.get_value()
        self.publisher = book_domain.publisher.get_value()
        self.authors = [au.get_value() for au in book_domain.authors.get_values()]
        self.published_at = book_domain.published_at
        self.tags = [TagAppModel(**vars(tag)) for tag in book_domain.tags.get_values()]


@dataclass(frozen=True)
class BookCreateAppModel:
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date


@dataclass(frozen=True)
class BookSearchIsbn13AppModel:
    isbn13: str


@dataclass(frozen=True)
class BookSearchBookIdAppModel:
    book_id: uuid.UUID


@dataclass(frozen=True)
class BookUpdateAppModel:
    book_id: uuid.UUID
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date


@dataclass(frozen=True)
class BookDeleteAppModel:
    book_id: uuid.UUID


@dataclass(frozen=True)
class BookTagsUpdateAppModel:
    book_id: uuid.UUID
    tag_ids: list[uuid.UUID]


class BookService:
    ENTITY_NAME: str = "Book"
    _book_repos: IBookRepository
    _book_factory: BookFactory
    _tag_repos: ITagRepository

    def __init__(self, book_repos: IBookRepository, tag_repos: ITagRepository):
        self._book_repos = book_repos
        self._book_factory = BookFactory(book_repos)
        self._tag_repos = tag_repos

    def list_by_isbn13(self, model: BookSearchIsbn13AppModel) -> list[BookAppModel]:
        isbn13 = ISBN13(model.isbn13)
        books = self._book_repos.find_by_isbn13(isbn13)
        if len(books) < 1:
            raise DataNotFoundError(str(model.isbn13), self.ENTITY_NAME, "list_by_isbn13")

        return [BookAppModel(book) for book in books]

    def find_by_book_id(self, model: BookSearchBookIdAppModel) -> BookAppModel:
        book = self._book_repos.find_by_id(model.book_id)
        if book is None:
            raise DataNotFoundError(str(model.book_id), self.ENTITY_NAME, "find_by_book_id")

        return BookAppModel(book)

    def create(self, model: BookCreateAppModel) -> BookAppModel:
        book = self._book_factory.create_new_book(
            model.isbn13,
            model.title,
            model.publisher,
            model.authors,
            model.published_at,
        )
        book = self._book_repos.create(book)
        return BookAppModel(book)

    def update_tags(self, model: BookTagsUpdateAppModel) -> None:
        current = self._book_repos.find_by_id(model.book_id)
        if not current:
            raise DataNotFoundError(str(id), self.ENTITY_NAME, "update")

        tags = []
        if len(model.tag_ids) > 0:
            tags = self._tag_repos.find_by_ids(model.tag_ids)
            if len(tags) != len(model.tag_ids):
                raise DataNotFoundError(str(id), self.ENTITY_NAME, "update_tags")

        self._book_repos.update_tags(current.book_id, model.tag_ids)
