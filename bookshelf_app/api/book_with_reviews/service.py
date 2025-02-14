import abc
import uuid
from dataclasses import dataclass
from datetime import date, datetime

from pydantic import UUID4

from bookshelf_app.api.shared.errors import AppValidationError


@dataclass(frozen=True)
class TagAppModel:
    name: str
    tag_id: UUID4


@dataclass(frozen=True)
class UserAppModel:
    user_id: UUID4
    name: str


@dataclass(frozen=True)
class ReviewAppModel:
    review_id: UUID4
    content: str
    is_draft: bool
    state: int
    completed_at: datetime | None
    last_modified_at: datetime
    user: UserAppModel


@dataclass(frozen=True)
class BookWithReviewsAppModel:
    book_id: UUID4
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date
    tags: list[TagAppModel]
    reviews: list[ReviewAppModel]


@dataclass(frozen=True)
class BooksWithReviewsAppModel:
    books_with_reviews: list[BookWithReviewsAppModel]


@dataclass(frozen=True)
class BookWithReviewLatestInputAppModel:
    max_count: int


def __post_init__(self):
    if self.max_count > 1000:
        raise AppValidationError("book review latest modified", f"not allowed over 1000 count:{self.max_count}")
    if self.max_count < 1:
        raise AppValidationError("book review latest modified", f"not allowed under 1 count:{self.max_count}")


@dataclass(frozen=True)
class BookWithReviewSearchUserIdAppModel:
    user_id: uuid.UUID


class IBookWithReviewsQueryService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_active_latest(self, max_count: int) -> BooksWithReviewsAppModel:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_active_by_user_id(self, user_id: uuid.UUID) -> BooksWithReviewsAppModel:
        raise NotImplementedError()


class BookWithReviewsService:
    ENTITY_NAME: str = "BookWithReviews"
    _query_service: IBookWithReviewsQueryService

    def __init__(self, query_service: IBookWithReviewsQueryService):
        self._query_service = query_service

    def list_active_latest(self, model: BookWithReviewLatestInputAppModel) -> BooksWithReviewsAppModel:
        return self._query_service.find_active_latest(model.max_count)

    def list_active_by_user_id(self, model: BookWithReviewSearchUserIdAppModel) -> BooksWithReviewsAppModel:
        return self._query_service.find_active_by_user_id(model.user_id)
