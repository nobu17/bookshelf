from datetime import datetime
from typing import Self

from fastapi import Depends, status
from pydantic import UUID4, BaseModel

from bookshelf_app.api.auth.service import TokenUserAppModel
from bookshelf_app.api.reviews.domain import ReviewStateEnum
from bookshelf_app.api.reviews.service import (
    BookReviewAppModel,
    BookReviewService,
    ReviewContentAppModel,
    ReviewCreateAppModel,
    ReviewDeleteAppModel,
    ReviewDetailCreateAppModel,
    ReviewDetailUpdateAppModel,
    ReviewStateUpdateAppModel,
    ReviewUpdateAppModel,
)
from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.infra.dependencies import (
    get_book_review_service,
    get_user_dependency,
)

router = CustomRouter()


class BookReviewBaseModel(BaseModel):
    book_id: UUID4
    content: str
    is_draft: bool
    state: int
    completed_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "60f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "content": "レビューとか感想とか",
                    "is_draft": False,
                    "state": 2,
                    "completed_at": "2032-04-23T10:20:30.400+02:30",
                }
            ]
        }
    }


class BookReviewCreateModel(BookReviewBaseModel):
    def to_app_model(self, user: TokenUserAppModel) -> ReviewCreateAppModel:
        content = ReviewContentAppModel(self.is_draft, self.content)
        state = ReviewStateUpdateAppModel(ReviewStateEnum.from_int(self.state), self.completed_at)
        detail = ReviewDetailCreateAppModel(state, content)
        model = ReviewCreateAppModel(user.user_id, self.book_id, detail)
        return model


class BookReviewUpdateModel(BaseModel):
    content: str
    is_draft: bool
    state: int
    completed_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "content": "レビューとか感想とか",
                    "is_draft": False,
                    "state": 2,
                    "completed_at": "2032-04-23T10:20:30.400+02:30",
                }
            ]
        }
    }

    def to_app_model(self, review_id: UUID4, user: TokenUserAppModel) -> ReviewUpdateAppModel:
        content = ReviewContentAppModel(self.is_draft, self.content)
        state = ReviewStateUpdateAppModel(ReviewStateEnum.from_int(self.state), self.completed_at)
        detail = ReviewDetailUpdateAppModel(review_id, state, content)
        model = ReviewUpdateAppModel(user.user_id, detail)
        return model


class BookReviewResponse(BookReviewBaseModel):
    review_id: UUID4
    last_modified_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "book_id": "60f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "content": "レビューとか感想とか",
                    "is_draft": False,
                    "state": 2,
                    "completed_at": "2032-04-23T10:20:30.400+02:30",
                    "last_modified_at": "2032-04-23T10:20:30.400+02:30",
                }
            ]
        }
    }

    @classmethod
    def from_app_model(cls, app_model: BookReviewAppModel) -> Self:
        model = cls(
            book_id=app_model.book_id,
            content=app_model.detail.content.value,
            is_draft=app_model.detail.content.is_draft,
            state=int(app_model.detail.state.state),
            completed_at=app_model.detail.state.completed_at,
            last_modified_at=app_model.detail.state.last_modified_at,
            review_id=app_model.detail.review_id,
        )

        return model


class BookReviewsResponse(BaseModel):
    reviews: list[BookReviewResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reviews": [
                        {
                            "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                            "book_id": "60f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                            "content": "レビューとか感想とか",
                            "is_draft": False,
                            "state": 2,
                            "completed_at": "2032-04-23T10:20:30.400+02:30",
                            "last_modified_at": "2032-04-23T10:20:30.400+02:30",
                        }
                    ]
                }
            ]
        }
    }


@router.get("/reviews/find", response_model=BookReviewResponse)
async def get_by_review_id(
    review_id: UUID4,
    review_service: BookReviewService = Depends(get_book_review_service),
) -> BookReviewResponse:
    result = review_service.find_by_review_id(review_id)
    return BookReviewResponse.from_app_model(result)


@router.get("/reviews/me", response_model=BookReviewsResponse)
async def get_my_reviews(
    review_service: BookReviewService = Depends(get_book_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BookReviewsResponse:
    result = review_service.find_by_user_id(user.user_id)
    reviews = [BookReviewResponse.from_app_model(x) for x in result.reviews]
    return BookReviewsResponse(reviews=reviews)


@router.get("/reviews/latest/{max_count}", response_model=BookReviewsResponse)
async def get_latest_reviews(
    max_count: int, review_service: BookReviewService = Depends(get_book_review_service)
) -> BookReviewsResponse:
    result = review_service.find_latest_modified(max_count)
    reviews = [BookReviewResponse.from_app_model(x) for x in result.reviews]
    return BookReviewsResponse(reviews=reviews)


@router.post("/reviews", response_model=BookReviewResponse)
async def create_review(
    body: BookReviewCreateModel,
    review_service: BookReviewService = Depends(get_book_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BookReviewResponse:
    app_model = body.to_app_model(user)
    result = review_service.create(app_model)
    return BookReviewResponse.from_app_model(result)


@router.put("/reviews/{review_id}", response_model=BookReviewResponse)
async def update_review(
    review_id: UUID4,
    body: BookReviewUpdateModel,
    review_service: BookReviewService = Depends(get_book_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BookReviewResponse:
    app_model = body.to_app_model(review_id, user)
    result = review_service.update(app_model)
    return BookReviewResponse.from_app_model(result)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    review_id: UUID4,
    review_service: BookReviewService = Depends(get_book_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
):
    app_model = ReviewDeleteAppModel(review_id, user.user_id, user.is_admin())
    review_service.delete(app_model)
    return
