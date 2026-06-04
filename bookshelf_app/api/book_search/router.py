from datetime import date

from fastapi import HTTPException
from pydantic import BaseModel

from bookshelf_app.api.book_search.service import (
    BookSearchRateLimitError,
    BookSearchResultAppModel,
    BookSearchService,
)
from bookshelf_app.api.shared.custom_router import CustomRouter

router = CustomRouter()


class BookSearchResultResponse(BaseModel):
    source: str
    source_id: str
    title: str
    authors: list[str]
    publisher: str
    isbn13: str
    published_at: date
    image_url: str | None = None
    description: str | None = None


class BookSearchResponse(BaseModel):
    books: list[BookSearchResultResponse]


@router.get("/book_search", response_model=BookSearchResponse)
async def search_books(keyword: str) -> BookSearchResponse:
    try:
        results = BookSearchService().search(keyword)
    except BookSearchRateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="外部書籍検索APIの利用制限に達しました。しばらく時間を置いてから再度お試しください。",
        ) from exc

    return BookSearchResponse(books=[convert(result) for result in results])


def convert(model: BookSearchResultAppModel) -> BookSearchResultResponse:
    return BookSearchResultResponse(**vars(model))
