import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self

from bookshelf_app.api.books.domain import IBookRepository
from bookshelf_app.api.reviews.domain import (
    BookReview,
    BookReviewUpdateParameter,
    IBookReviewRepository,
    ReviewContent,
    ReviewDetail,
    ReviewState,
    ReviewStateEnum,
)
from bookshelf_app.api.shared.errors import (
    AppValidationError,
    DataNotFoundError,
    InvalidAuthError,
)


@dataclass(frozen=False)
class ReviewStateAppModel:
    state: ReviewStateEnum
    completed_at: datetime | None
    last_modified_at: datetime


@dataclass(frozen=False)
class ReviewContentAppModel:
    is_draft: bool
    value: str

    def to_domain(self) -> ReviewContent:
        content = ReviewContent(self.value, self.is_draft)
        return content

    @classmethod
    def from_domain(cls, domain: ReviewContent) -> Self:
        instance = cls(is_draft=domain.is_draft, value=domain.get_value())
        return instance


@dataclass(frozen=False)
class ReviewDetailAppModel:
    review_id: uuid.UUID
    state: ReviewStateAppModel
    content: ReviewContentAppModel

    def __init__(self, review_domain: ReviewDetail):
        self.review_id = review_domain.review_id
        self.state = ReviewStateAppModel(**vars(review_domain.state))
        self.content = ReviewContentAppModel.from_domain(review_domain.content)


@dataclass(frozen=False)
class BookReviewAppModel:
    user_id: uuid.UUID
    book_id: uuid.UUID
    detail: ReviewDetailAppModel

    def __init__(self, review_domain: BookReview):
        self.user_id = review_domain.user_id
        self.book_id = review_domain.book_id
        self.detail = ReviewDetailAppModel(review_domain.detail)


@dataclass(frozen=False)
class BookReviewsAppModel:
    reviews: list[BookReviewAppModel]


@dataclass(frozen=False)
class ReviewStateUpdateAppModel:
    state: ReviewStateEnum
    completed_at: datetime | None

    def to_domain(self) -> ReviewState:
        state = ReviewState()
        return state.update(self.state, self.completed_at)


@dataclass(frozen=False)
class ReviewDetailCreateAppModel:
    state: ReviewStateUpdateAppModel
    content: ReviewContentAppModel

    def to_domain(self) -> ReviewDetail:
        state = self.state.to_domain()
        content = self.content.to_domain()
        detail = ReviewDetail(state, content)
        return detail


@dataclass(frozen=False)
class ReviewCreateAppModel:
    user_id: uuid.UUID
    book_id: uuid.UUID
    detail: ReviewDetailCreateAppModel

    def to_domain(self) -> BookReview:
        detail = self.detail.to_domain()
        domain_review = BookReview(self.user_id, self.book_id, detail)
        return domain_review


@dataclass(frozen=False)
class ReviewDetailUpdateAppModel:
    review_id: uuid.UUID
    state: ReviewStateUpdateAppModel
    content: ReviewContentAppModel

    def to_domain(self) -> ReviewDetail:
        state = self.state.to_domain()
        content = self.content.to_domain()
        detail = ReviewDetail.create_with_id(self.review_id, state, content)
        return detail


@dataclass(frozen=False)
class ReviewUpdateAppModel:
    user_id: uuid.UUID
    detail: ReviewDetailUpdateAppModel

    def to_domain(self) -> BookReviewUpdateParameter:
        update_parameter = BookReviewUpdateParameter(
            self.detail.state.state,
            self.detail.state.completed_at,
            self.detail.content.value,
            self.detail.content.is_draft,
        )
        return update_parameter


@dataclass(frozen=False)
class ReviewDeleteAppModel:
    review_id: uuid.UUID
    user_id: uuid.UUID
    is_admin: bool


class BookReviewService:
    ENTITY_NAME: str = "BookReview"
    _review_repos: IBookReviewRepository
    _book_repos: IBookRepository

    def __init__(self, review_repos: IBookReviewRepository, book_repos: IBookRepository):
        self._review_repos = review_repos
        self._book_repos = book_repos

    def find_by_review_id(self, id: uuid.UUID) -> BookReviewAppModel:
        review = self._review_repos.find_by_review_id(id)
        if review is None:
            raise DataNotFoundError(str(id), self.ENTITY_NAME, "find_by_review_id")

        return BookReviewAppModel(review)

    def find_by_user_id(self, id: uuid.UUID) -> BookReviewsAppModel:
        reviews = self._review_repos.find_by_user_id(id)

        return BookReviewsAppModel([BookReviewAppModel(x) for x in reviews.reviews])

    def find_latest_modified(self, max_count: int) -> BookReviewsAppModel:
        if max_count > 1000:
            raise AppValidationError("book review latest modified", f"not allowed over 1000 count:{max_count}")
        if max_count < 1:
            raise AppValidationError("book review latest modified", f"not allowed under 1 count:{max_count}")

        reviews = self._review_repos.find_latest_modified(max_count)

        return BookReviewsAppModel([BookReviewAppModel(x) for x in reviews.reviews])

    def create(self, create_data: ReviewCreateAppModel) -> BookReviewAppModel:
        book = self._book_repos.find_by_id(create_data.book_id)
        if book is None:
            raise AppValidationError("book review create", f"book is not exists. book_id:{create_data.book_id}")

        domain_review = create_data.to_domain()
        user_reviews = self._review_repos.find_by_user_id_and_book_id(create_data.user_id, create_data.book_id)
        user_reviews.add(domain_review)

        created = self._review_repos.create(user_reviews.last_modified)
        return BookReviewAppModel(created)

    def update(self, update_data: ReviewUpdateAppModel) -> BookReviewAppModel:
        update_parameter = update_data.to_domain()
        review = self._review_repos.find_by_review_id(update_data.detail.review_id)
        if review is None:
            raise AppValidationError(
                "book review update", f"review is not exists. review_id:{update_data.detail.review_id}"
            )

        updated_review = review.update(update_parameter)
        user_reviews = self._review_repos.find_by_user_id_and_book_id(updated_review.user_id, updated_review.book_id)
        user_reviews.update(updated_review)

        updated = self._review_repos.update(user_reviews.last_modified)
        return BookReviewAppModel(updated)

    def delete(self, delete_info: ReviewDeleteAppModel) -> None:
        review = self._review_repos.find_by_review_id(delete_info.review_id)
        if review is None:
            raise DataNotFoundError(str(id), self.ENTITY_NAME, "delete")
        # check owner
        if not delete_info.is_admin:
            if not review.is_same_user(delete_info.user_id):
                raise InvalidAuthError("try to remove another user data.")

        self._review_repos.delete(delete_info.review_id)
