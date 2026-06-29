from datetime import date

from fastapi import Depends, Query
from pydantic import UUID4, BaseModel, ConfigDict

from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.api.tags.router import TagResponse
from bookshelf_app.infra.dependencies import get_admin_dependency, get_book_service, get_user_dependency

from .service import (
    BookAppModel,
    BookCreateAppModel,
    BookMasterAppModel,
    BookMasterSearchAppModel,
    BookSearchBookIdAppModel,
    BookSearchIsbn13AppModel,
    BookService,
    BookTagsUpdateAppModel,
    BookUpdateAppModel,
)

router = CustomRouter()


class BookBaseModel(BaseModel):
    isbn13: str
    title: str
    publisher: str
    authors: list[str]
    published_at: date
    image_url: str = ""


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
                    "published_at": "2023-01-10",
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
                            "published_at": "2023-01-10",
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


class BookMasterResponse(BookResponse):
    review_count: int


class BookMastersResponse(BaseModel):
    books: list[BookMasterResponse]


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


class BookUpdateModel(BookBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "isbn13": "9784814400690",
                    "title": "入門 継続的デリバリー 改訂版",
                    "publisher": "オライリージャパン",
                    "authors": ["著者1", "著者2"],
                    "published_at": "2023-01-10",
                    "image_url": "https://example.com/cover.jpg",
                }
            ]
        },
    )


class BookTagUpdateModel(BaseModel):
    tag_ids: list[UUID4]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "tag_ids": [
                        "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d83",
                        "4b4b6c77-6825-4a2d-8ae9-0d431e8d8d85",
                    ],
                }
            ]
        },
    )


@router.get("/books", response_model=BookMastersResponse, dependencies=[Depends(get_admin_dependency)])
def search_book_masters(
    keyword: str = "",
    max_count: int = Query(default=100, ge=1, le=500),
    book_service: BookService = Depends(get_book_service),
) -> BookMastersResponse:
    results = book_service.search_masters(BookMasterSearchAppModel(keyword=keyword, max_count=max_count))
    return BookMastersResponse(books=[create_master_from_model(result) for result in results])


@router.post("/books", response_model=BookResponse, dependencies=[Depends(get_user_dependency)])
def create_book(
    body: BookCreateModel,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    result = book_service.create(BookCreateAppModel(**vars(body)))
    return create_from_model(result)


@router.get("/books/isbn13/{isbn13}", response_model=BooksResponse)
def find_books_by_isbn13(
    isbn13: str,
    book_service: BookService = Depends(get_book_service),
) -> BooksResponse:
    model = BookSearchIsbn13AppModel(isbn13)
    results = book_service.list_by_isbn13(model)
    return BooksResponse(books=[create_from_model(result) for result in results])


@router.get("/books/book_id/{book_id}", response_model=BookResponse)
def find_book_by_book_id(
    book_id: UUID4,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    model = BookSearchBookIdAppModel(book_id)
    result = book_service.find_by_book_id(model)
    return create_from_model(result)


@router.put("/books/{book_id}", response_model=BookResponse, dependencies=[Depends(get_admin_dependency)])
def update_book(
    book_id: UUID4,
    body: BookUpdateModel,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    result = book_service.update(BookUpdateAppModel(book_id=book_id, **vars(body)))
    return create_from_model(result)


@router.put("/books/tags/{book_id}", response_model=None, dependencies=[Depends(get_user_dependency)])
def update_book_tags(
    book_id: UUID4,
    body: BookTagUpdateModel,
    book_service: BookService = Depends(get_book_service),
) -> None:
    book_service.update_tags(BookTagsUpdateAppModel(book_id=book_id, **vars(body)))


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
        image_url=model.image_url,
        authors=model.authors,
        tags=tags,
    )


def create_master_from_model(model: BookMasterAppModel) -> BookMasterResponse:
    base = create_from_model(model)
    return BookMasterResponse(**vars(base), review_count=model.review_count)
