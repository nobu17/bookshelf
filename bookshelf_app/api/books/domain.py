import abc
import re
import uuid
from datetime import date
from typing import Self

from bookshelf_app.api.reviews.domain import BookReview
from bookshelf_app.api.shared.domain import StringLimitValueObject
from bookshelf_app.api.shared.errors import DomainValidationError
from bookshelf_app.api.tags.domain import Tag


class ISBN13:
    value: str

    def __init__(self, value: str):
        self.value = value
        self._validate()

    def _validate(self):
        if not self.value:
            raise DomainValidationError(self.__class__.__name__, "value is empty")
        if len(self.value) != 13:
            raise DomainValidationError(self.__class__.__name__, "value length should be 13")
        if not self.value.startswith("978") and not self.value.startswith("979"):
            raise DomainValidationError(self.__class__.__name__, "value should be start with 978 or 979")
        if not re.fullmatch("[0-9]+", self.value):
            raise DomainValidationError(self.__class__.__name__, "value should be only numeric")

        self._check_digits()

    def _check_digits(self):
        strs = list(self.value)
        current_digit = 13
        odd_total = 0
        even_total = 0
        for s in strs:
            num = int(s)
            # skip check digit
            if current_digit == 1:
                break
            if current_digit % 2 == 0:
                even_total += num
            else:
                odd_total += num

            current_digit -= 1

        calc_total = (even_total * 3) + odd_total
        check_digit = (10 - (calc_total % 10)) % 10

        if int(strs[12]) != check_digit:
            raise DomainValidationError(
                self.__class__.__name__, f"invalid check digits. actual:{strs[12]}, expected:{str(check_digit)}"
            )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ISBN13):
            return self.value == other.value
        return False


class BookTitle(StringLimitValueObject):
    def __init__(self, value: str):
        super().__init__(100, value)


class Publisher(StringLimitValueObject):
    def __init__(self, value: str):
        super().__init__(100, value)


class Author(StringLimitValueObject):
    def __init__(self, value: str):
        super().__init__(100, value)


class Authors:
    _values: list[Author]

    def __init__(self, values: list[Author]):
        self._values = values
        self._validate()

    def _validate(self):
        if len(self._values) < 1:
            raise DomainValidationError(self.__class__.__name__, "empty values")

    def get_values(self) -> list[Author]:
        return [Author(x.get_value()) for x in self._values]


class Tags:
    _values: list[Tag]

    def __init__(self, values: list[Tag]):
        self._values = values
        self._validate()

    def _validate(self):
        pass  # currently allow empty

    def get_values(self) -> list[Tag]:
        return [Tag(x.name) for x in self._values]


class Book:
    book_id: uuid.UUID
    isbn13: ISBN13
    title: BookTitle
    publisher: Publisher
    authors: Authors
    published_at: date
    tags: Tags

    def __init__(
        self,
        isbn13: ISBN13,
        title: BookTitle,
        publisher: Publisher,
        authors: Authors,
        published_at: date,
        tags: Tags,
    ):
        self.book_id = uuid.uuid4()
        self.isbn13 = isbn13
        self.title = title
        self.publisher = publisher
        self.authors = authors
        self.published_at = published_at
        self.tags = tags

    @classmethod
    def create_for_orm(
        cls,
        book_id: uuid.UUID,
        isbn13: ISBN13,
        title: BookTitle,
        publisher: Publisher,
        authors: Authors,
        published_at: date,
        tags: Tags,
    ) -> Self:
        instance = cls(isbn13, title, publisher, authors, published_at, tags)
        instance.book_id = book_id
        return instance

    def __eq__(self, other: object) -> bool:
        # same isbn and same year book treats as same book
        if isinstance(other, Book):
            return self.isbn13 == other.isbn13 and self.published_at.year == other.published_at.year
        return False


class BookWithReviews:
    book: Book
    reviews: list[BookReview]

    def __init__(self, book: Book, reviews: list[BookReview]):
        self.book = book
        self.reviews = reviews

    @classmethod
    def create_for_orm(
        cls,
        book: Book,
        reviews: list[BookReview],
    ) -> Self:
        instance = cls(book, reviews)
        return instance


class IBookRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_by_isbn13(self, isbn13: ISBN13) -> list[Book]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, id: uuid.UUID) -> Book | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, item: Book) -> Book:
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, item: Book) -> Book:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_tags(self, id: uuid.UUID, tag_ids: list[uuid.UUID]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_with_reviews_by_user_id(self, user_id: uuid.UUID) -> list[BookWithReviews]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_with_latest_reviews(self, max_count: int) -> list[BookWithReviews]:
        raise NotImplementedError()


class BookFactory:
    _book_repos: IBookRepository

    def __init__(self, book_repos: IBookRepository):
        self._book_repos = book_repos

    def create_new_book(self, isbn13: str, title: str, publisher: str, authors: list[str], published_at: date) -> Book:
        isbn13_d = ISBN13(isbn13)
        title_d = BookTitle(title)
        publisher_d = Publisher(publisher)

        auth_list = [Author(au) for au in authors]
        authors_d = Authors(auth_list)

        book = Book(isbn13_d, title_d, publisher_d, authors_d, published_at, Tags([]))

        if self.is_same_book_existed(book):
            raise DomainValidationError(
                "book", f"same book is already existed. isbn13:{book.isbn13.value}, published_at:{book.published_at}"
            )

        return book

    def is_same_book_existed(self, check_book: Book) -> bool:
        # try to get same isbn book
        same_isbn_books = self._book_repos.find_by_isbn13(check_book.isbn13)
        if len(same_isbn_books) == 0:
            return False

        for b in same_isbn_books:
            if b == check_book:
                return True

        return False
