from uuid import uuid4

import pytest

from bookshelf_app.api.reviews.domain import BookReview, ReviewContent, ReviewDetail, ReviewState, ReviewStateEnum
from bookshelf_app.api.reviews.service import (
    BookReviewService,
    ReviewContentAppModel,
    ReviewDetailUpdateAppModel,
    ReviewStateUpdateAppModel,
    ReviewUpdateAppModel,
)
from bookshelf_app.api.shared.errors import InvalidAuthError


def test_review_update_denies_another_user_data():
    review_owner_id = uuid4()
    request_user_id = uuid4()
    book_id = uuid4()
    review = BookReview(
        review_owner_id,
        book_id,
        ReviewDetail(ReviewState(), ReviewContent("owner review", False)),
    )
    service = BookReviewService(FakeReviewRepository(review), FakeBookRepository())
    update_model = ReviewUpdateAppModel(
        request_user_id,
        ReviewDetailUpdateAppModel(
            review.detail.review_id,
            ReviewStateUpdateAppModel(ReviewStateEnum.NOT_YET, None),
            ReviewContentAppModel(False, "updated by another user"),
        ),
    )

    with pytest.raises(InvalidAuthError):
        service.update(update_model)


class FakeReviewRepository:
    def __init__(self, review: BookReview):
        self._review = review
        self.update_called = False

    def find_by_review_id(self, _id):
        return self._review

    def find_by_user_id_and_book_id(self, _user_id, _book_id):
        raise AssertionError("should not load user reviews for another user's update")

    def update(self, _review):
        self.update_called = True
        raise AssertionError("should not update another user's review")


class FakeBookRepository:
    pass
