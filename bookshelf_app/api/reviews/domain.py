import abc
import uuid
from datetime import datetime
from enum import IntEnum
from typing import Self

from bookshelf_app.api.shared.domain import StringAllowEmptyLimitValueObject
from bookshelf_app.api.shared.errors import DomainValidationError
from bookshelf_app.api.shared.helper import TimeUtil


class ReviewStateEnum(IntEnum):
    NOT_YET = 0
    IN_PROGRESS = 1
    COMPLETED = 2

    @staticmethod
    def from_int(val: int) -> "ReviewStateEnum":
        if ReviewStateEnum.NOT_YET == val:
            return ReviewStateEnum.NOT_YET
        if ReviewStateEnum.IN_PROGRESS == val:
            return ReviewStateEnum.IN_PROGRESS
        if ReviewStateEnum.COMPLETED == val:
            return ReviewStateEnum.COMPLETED

        raise DomainValidationError("ReviewStateEnum", f"convert is failed from int. value:{val}")

    def __int__(self):
        return self.value


class ReviewState:
    state: ReviewStateEnum
    completed_at: datetime | None
    last_modified_at: datetime

    def __init__(self):
        self.state = ReviewStateEnum.NOT_YET
        self.last_modified_at = TimeUtil.get_now()
        self.completed_at = None

    def update(self, state: ReviewStateEnum, completed_at: datetime | None) -> "ReviewState":
        if state == ReviewStateEnum.IN_PROGRESS:
            return self._change_in_progress()
        elif state == ReviewStateEnum.COMPLETED:
            if completed_at is None:
                raise DomainValidationError("ReviewState", "try to set completed. but datetime is none.")
            return self._change_completed(completed_at)
        else:
            return self._change_not_yet()

    def _change_not_yet(self) -> "ReviewState":
        state = ReviewState()
        state.state = ReviewStateEnum.NOT_YET
        state.last_modified_at = TimeUtil.get_now()
        state.completed_at = None
        return state

    def _change_in_progress(self) -> "ReviewState":
        state = ReviewState()
        state.state = ReviewStateEnum.IN_PROGRESS
        state.last_modified_at = TimeUtil.get_now()
        state.completed_at = None
        return state

    def _change_completed(self, completed_at: datetime) -> "ReviewState":
        state = ReviewState()
        state.state = ReviewStateEnum.COMPLETED
        state.last_modified_at = TimeUtil.get_now()
        state.completed_at = TimeUtil.get_jst(completed_at)
        return state

    @classmethod
    def create_from_orm(cls, state: ReviewStateEnum, completed_at: datetime | None, last_modified_at: datetime) -> Self:
        instance = cls()
        instance.state = state
        instance.completed_at = completed_at
        instance.last_modified_at = last_modified_at
        return instance


class ReviewContent(StringAllowEmptyLimitValueObject):
    is_draft: bool

    def __init__(self, value: str, is_draft: bool):
        super().__init__(10000, value)
        self.is_draft = is_draft

    def update(self, content: str, is_draft: bool) -> "ReviewContent":
        return ReviewContent(content, is_draft)

    @classmethod
    def create_from_orm(cls, value: str, is_draft: bool) -> Self:
        instance = cls(value, is_draft)
        return instance


class BookReviewUpdateParameter:
    state: ReviewStateEnum
    completed_at: datetime | None
    content: str
    is_draft: bool

    def __init__(self, state: ReviewStateEnum, completed_at: datetime | None, content: str, is_draft: bool):
        self.state = state
        self.completed_at = completed_at
        self.content = content
        self.is_draft = is_draft


class ReviewDetail:
    review_id: uuid.UUID
    state: ReviewState
    content: ReviewContent

    def __init__(self, state: ReviewState, content: ReviewContent):
        self.review_id = uuid.uuid4()
        self.state = state
        self.content = content

    def update(self, parameter: BookReviewUpdateParameter) -> "ReviewDetail":
        state = self.state.update(parameter.state, parameter.completed_at)
        content = self.content.update(parameter.content, parameter.is_draft)
        new_data = ReviewDetail(state, content)
        new_data.review_id = self.review_id
        return new_data

    @classmethod
    def create_with_id(cls, review_id: uuid.UUID, state: ReviewState, content: ReviewContent) -> Self:
        instance = cls(state, content)
        instance.review_id = review_id
        return instance

    @classmethod
    def create_from_orm(cls, review_id: uuid.UUID, state: ReviewState, content: ReviewContent) -> Self:
        instance = cls(state, content)
        instance.review_id = review_id
        return instance


class BookReview:
    user_id: uuid.UUID
    book_id: uuid.UUID
    detail: ReviewDetail

    def __init__(self, user_id: uuid.UUID, book_id: uuid.UUID, detail: ReviewDetail):
        if detail is None:
            raise DomainValidationError(self.__class__.__name__, "empty details")

        self.user_id = user_id
        self.book_id = book_id
        self.detail = detail

    def is_same_user(self, user_id: uuid.UUID):
        return self.user_id == user_id

    @classmethod
    def create_from_orm(
        cls,
        detail: ReviewDetail,
        user_id: uuid.UUID,
        book_id: uuid.UUID,
    ) -> Self:
        instance = cls(user_id, book_id, detail)
        return instance

    def update(self, parameter: BookReviewUpdateParameter) -> "BookReview":
        instance = BookReview(self.user_id, self.book_id, self.detail)
        instance.detail = self.detail.update(parameter)
        return instance


class BookReviews:
    reviews: list[BookReview]

    def __init__(self):
        self.reviews = []

    @classmethod
    def create_from_orm(
        cls,
        reviews: list[BookReview],
    ) -> Self:
        instance = cls()
        instance.reviews = reviews

        return instance


class IBookReviewRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_by_review_id(self, id: uuid.UUID) -> BookReview | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_user_id(self, id: uuid.UUID) -> BookReviews:
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, review: BookReview) -> BookReview:
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, review: BookReview) -> BookReview:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError()
