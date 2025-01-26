from datetime import date

from fastapi import Depends
from pydantic import UUID4, BaseModel

from bookshelf_app.api.auth.service import TokenUserAppModel
from bookshelf_app.api.reviews.router import BookReviewResponse
from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.api.tags.router import TagResponse
from bookshelf_app.infra.dependencies import get_book_service, get_user_dependency

from .service import (
    BookAppModel,
    BookCreateAppModel,
    BookSearchBookIdAppModel,
    BookSearchIsbn13AppModel,
    BookService,
    BookTagsUpdateAppModel,
    BookWithReviewsAppModel,
    BookWithReviewSearchUserIdAppModel,
)

router = CustomRouter()


class BookBaseModel(BaseModel):
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date


class BookResponse(BookBaseModel):
    book_id: UUID4
    tags: list[TagResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                    "isbn13": "9784814400690",
                    "title": "入門 継続的デリバリー",
                    "publisher": "オライリージャパン",
                    "authors": ["著者1", "著者2"],
                    "published_at": "2023/01/10",
                    "tags": [
                        {
                            "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                            "name": "DevOps",
                        }
                    ],
                }
            ]
        }
    }


class BooksResponse(BaseModel):
    books: list[BookResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "books": [
                        {
                            "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                            "isbn13": "9784814400690",
                            "title": "入門 継続的デリバリー",
                            "publisher": "オライリージャパン",
                            "authors": ["著者1", "著者2"],
                            "published_at": "2023/01/10",
                            "tags": [
                                {
                                    "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "name": "DevOps",
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    }


class BookWithReviewsResponse(BookResponse):
    reviews: list[BookReviewResponse]


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
                            "published_at": "2023/01/10",
                            "tags": [
                                {
                                    "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "name": "DevOps",
                                }
                            ],
                            "reviews": [
                                {
                                    "review_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                                    "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                                    "content": "レビューとか感想とか",
                                    "is_draft": False,
                                    "state": 2,
                                    "completed_at": "2032-04-23T10:20:30.400+02:30",
                                    "last_modified_at": "2032-04-23T10:20:30.400+02:30",
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    }


class BookCreateModel(BookBaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "isbn13": "9784814400690",
                    "title": "入門 継続的デリバリー",
                    "publisher": "オライリージャパン",
                    "authors": ["著者1", "著者2"],
                    "published_at": "2023-01-10",
                }
            ]
        }
    }


class BookTagUpdateModel(BaseModel):
    book_id: UUID4
    tag_ids: list[UUID4]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                    "tag_ids": [
                        "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                        "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d85",
                    ],
                }
            ]
        }
    }


@router.post("/books", response_model=BookResponse, dependencies=[Depends(get_user_dependency)])
async def create_book(
    body: BookCreateModel,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    result = book_service.create(BookCreateAppModel(**vars(body)))
    return create_from_model(result)


@router.get("/books/isbn13/{isbn13}", response_model=BooksResponse)
async def find_books_by_isbn13(
    isbn13: str,
    book_service: BookService = Depends(get_book_service),
) -> BooksResponse:
    model = BookSearchIsbn13AppModel(isbn13)
    results = book_service.list_by_isbn13(model)
    return BooksResponse(books=[create_from_model(result) for result in results])


@router.get("/books/book_id/{book_id}", response_model=BookResponse)
async def find_book_by_book_id(
    book_id: UUID4,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    model = BookSearchBookIdAppModel(book_id)
    result = book_service.find_by_book_id(model)
    return create_from_model(result)


@router.get("/books/reviews/user_id/{user_id}", response_model=BooksWithReviewsResponse)
async def find_books_with_reviews_by_user_id(
    user_id: UUID4,
    book_service: BookService = Depends(get_book_service),
) -> BooksWithReviewsResponse:
    model = BookWithReviewSearchUserIdAppModel(user_id)
    results = book_service.list_with_reviews_by_user_id(model)
    books_with_reviews = [create_with_reviews_from_model(result) for result in results]
    return BooksWithReviewsResponse(books_with_reviews=books_with_reviews)


@router.get("/books/reviews/me", response_model=BooksWithReviewsResponse)
async def find_books_with_my_reviews(
    book_service: BookService = Depends(get_book_service),
    user: TokenUserAppModel = Depends(get_user_dependency),
) -> BooksWithReviewsResponse:
    model = BookWithReviewSearchUserIdAppModel(user.user_id)
    results = book_service.list_with_reviews_by_user_id(model)
    books_with_reviews = [create_with_reviews_from_model(result) for result in results]
    return BooksWithReviewsResponse(books_with_reviews=books_with_reviews)


@router.put("/books/tags/{id}", response_model=None, dependencies=[Depends(get_user_dependency)])
async def update_book_tags(
    body: BookTagUpdateModel,
    book_service: BookService = Depends(get_book_service),
) -> None:
    book_service.update_tags(BookTagsUpdateAppModel(**vars(body)))


def create_from_model(model: BookAppModel) -> BookResponse:
    tags = []
    for tag in model.tags:
        tags.append(TagResponse(**vars(tag)))
    return BookResponse(
        book_id=model.book_id,
        isbn13=model.isbn13,
        title=model.title,
        publisher=model.publisher,
        published_at=model.published_at,
        authors=model.authors,
        tags=tags,
    )


def create_with_reviews_from_model(model: BookWithReviewsAppModel) -> BookWithReviewsResponse:
    tags = []
    for tag in model.book.tags:
        tags.append(TagResponse(**vars(tag)))

    reviews = [BookReviewResponse.from_app_model(review) for review in model.reviews]
    return BookWithReviewsResponse(
        book_id=model.book.book_id,
        isbn13=model.book.isbn13,
        title=model.book.title,
        publisher=model.book.publisher,
        published_at=model.book.published_at,
        authors=model.book.authors,
        tags=tags,
        reviews=reviews,
    )
