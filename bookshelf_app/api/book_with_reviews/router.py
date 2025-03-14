from datetime import date, datetime

from fastapi import Depends
from pydantic import UUID4, BaseModel

from bookshelf_app.api.auth.service import TokenUserAppModel
from bookshelf_app.api.book_with_reviews.service import (
    BooksWithReviewsAppModel,
    BookWithReviewLatestInputAppModel,
    BookWithReviewsAppModel,
    BookWithReviewSearchUserIdAndBookIdAppModel,
    BookWithReviewSearchUserIdAppModel,
    BookWithReviewsService,
)
from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.infra.dependencies import (
    get_book_with_review_service,
    get_user_dependency,
)

router = CustomRouter()


class TagResponse(BaseModel):
    name: str
    tag_id: UUID4


class UserResponse(BaseModel):
    user_id: UUID4
    name: str


class ReviewResponse(BaseModel):
    review_id: UUID4
    content: str
    is_draft: bool
    state: int
    completed_at: datetime | None = None
    last_modified_at: datetime
    user: UserResponse


class BookWithReviewsResponse(BaseModel):
    book_id: UUID4
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date
    tags: list[TagResponse]
    reviews: list[ReviewResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                [
                    {
                        "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                        "isbn13": "9784814400690",
                        "title": "入門 継続的デリバリー",
                        "publisher": "オライリージャパン",
                        "authors": ["著者1", "著者2"],
                        "published_at": "2023-01-10",
                        "tags": [
                            {
                                "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                "name": "DevOps",
                            }
                        ],
                        "reviews": [
                            {
                                "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                "content": "レビューとか感想とか",
                                "is_draft": False,
                                "state": 2,
                                "completed_at": "2032-04-23T10:20:30.400+02:30",
                                "last_modified_at": "2032-04-23T10:20:30.400+02:30",
                                "user": {
                                    "user_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "name": "user",
                                },
                            }
                        ],
                    }
                ]
            ]
        }
    }


class BooksWithReviewsResponse(BaseModel):
    books_with_reviews: list[BookWithReviewsResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "books_with_reviews": [
                        {
                            "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                            "isbn13": "9784814400690",
                            "title": "入門 継続的デリバリー",
                            "publisher": "オライリージャパン",
                            "authors": ["著者1", "著者2"],
                            "published_at": "2023-01-10",
                            "tags": [
                                {
                                    "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "name": "DevOps",
                                }
                            ],
                            "reviews": [
                                {
                                    "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "content": "レビューとか感想とか",
                                    "is_draft": False,
                                    "state": 2,
                                    "completed_at": "2032-04-23T10:20:30.400+02:30",
                                    "last_modified_at": "2032-04-23T10:20:30.400+02:30",
                                    "user": {
                                        "user_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                        "name": "user",
                                    },
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    }


@router.get("/book_with_reviews/latest/{max_count}", response_model=BooksWithReviewsResponse)
async def find_books_with_latest_reviews(
    max_count: int,
    service: BookWithReviewsService = Depends(get_book_with_review_service),
) -> BooksWithReviewsResponse:
    input_model = BookWithReviewLatestInputAppModel(max_count)
    out_model = service.list_active_latest(input_model)
    return BooksWithReviewsResponse(books_with_reviews=_convert(out_model))


@router.get("/book_with_reviews/user_id/{user_id}", response_model=BooksWithReviewsResponse)
async def find_books_with_reviews_by_user_id(
    user_id: UUID4,
    service: BookWithReviewsService = Depends(get_book_with_review_service),
) -> BooksWithReviewsResponse:
    model = BookWithReviewSearchUserIdAppModel(user_id)
    out_model = service.list_active_by_user_id(model)
    return BooksWithReviewsResponse(books_with_reviews=_convert(out_model))


@router.get("/book_with_reviews/me", response_model=BooksWithReviewsResponse)
async def find_books_with_my_reviews(
    service: BookWithReviewsService = Depends(get_book_with_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BooksWithReviewsResponse:
    model = BookWithReviewSearchUserIdAppModel(user.user_id)
    out_model = service.list_active_by_user_id(model)
    return BooksWithReviewsResponse(books_with_reviews=_convert(out_model))


@router.get("/book_with_reviews/for_edit/me", response_model=BooksWithReviewsResponse)
async def find_books_for_edit_with_my_reviews(
    service: BookWithReviewsService = Depends(get_book_with_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BooksWithReviewsResponse:
    model = BookWithReviewSearchUserIdAppModel(user.user_id)
    out_model = service.list_by_user_id(model)
    return BooksWithReviewsResponse(books_with_reviews=_convert(out_model))


@router.get("/book_with_reviews/for_edit/book_id/{book_id}", response_model=BookWithReviewsResponse)
async def find_specific_book_for_edit_with_my_reviews(
    book_id: UUID4,
    service: BookWithReviewsService = Depends(get_book_with_review_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BookWithReviewsResponse:
    model = BookWithReviewSearchUserIdAndBookIdAppModel(user.user_id, book_id)
    out_model = service.find_by_user_id_and_book_id(model)
    return _convert_book_with_review(out_model)


# pylint: disable=too-many-function-args
def _convert(out_model: BooksWithReviewsAppModel) -> list[BookWithReviewsResponse]:
    book_with_reviews: list[BookWithReviewsResponse] = []
    for model in out_model.books_with_reviews:
        book_with_review = _convert_book_with_review(model)
        book_with_reviews.append(book_with_review)

    return book_with_reviews


# pylint: disable=too-many-function-args
def _convert_book_with_review(model: BookWithReviewsAppModel) -> BookWithReviewsResponse:
    tags = [TagResponse(**vars(x)) for x in model.tags]
    reviews = [
        ReviewResponse(
            review_id=x.review_id,
            content=x.content,
            is_draft=x.is_draft,
            state=x.state,
            completed_at=x.completed_at,
            last_modified_at=x.last_modified_at,
            user=UserResponse(**vars(x.user)),
        )
        for x in model.reviews
    ]
    return BookWithReviewsResponse(
        book_id=model.book_id,
        isbn13=model.isbn13,
        title=model.title,
        publisher=model.publisher,
        authors=model.authors,
        published_at=model.published_at,
        tags=tags,
        reviews=reviews,
    )
