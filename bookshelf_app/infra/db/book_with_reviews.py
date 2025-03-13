from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Mapped, Session, contains_eager, joinedload, relationship
from sqlalchemy.sql.expression import false

from bookshelf_app.api.book_with_reviews.service import (
    BooksWithReviewsAppModel,
    BookWithReviewsAppModel,
    IBookWithReviewsQueryService,
    ReviewAppModel,
    TagAppModel,
    UserAppModel,
)

from .auth import UserDTO
from .books import BookDTO
from .reviews import BookReviewDTO


# pylint: disable=unsubscriptable-object
class BookReviewExtendDTO(BookReviewDTO):
    ex_user: Mapped[UserDTO] = relationship()

    def to_response(self) -> ReviewAppModel:

        user = UserAppModel(self.ex_user.user_id, self.ex_user.name)
        resp = ReviewAppModel(
            self.review_id, self.content, self.is_draft, self.state, self.completed_at, self.last_modified_at, user
        )
        return resp


# pylint: disable=unsubscriptable-object
class BookExtendDTO(BookDTO):
    ex_reviews: Mapped[list[BookReviewExtendDTO]] = relationship()

    def to_response(self) -> BookWithReviewsAppModel:
        tag_list: list[TagAppModel] = []
        for tag in self.filter_deleted_tags():
            tag_resp = TagAppModel(tag.name, tag.tag_id)
            tag_list.append(tag_resp)

        resp = BookWithReviewsAppModel(
            self.book_id,
            self.isbn13,
            self.title,
            self.publisher.name,
            [x.name for x in self.authors],
            self.published_at,
            tag_list,
            [x.to_response() for x in self.ex_reviews],
        )
        return resp


class SqlBookWithQueryService(IBookWithReviewsQueryService):
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def find_active_latest(self, max_count: int) -> BooksWithReviewsAppModel:
        stmt = (
            select(BookExtendDTO)
            .join(BookReviewExtendDTO)
            .options(
                joinedload(BookExtendDTO.authors),
                joinedload(BookExtendDTO.publisher),
                joinedload(BookExtendDTO.tags),
                contains_eager(BookExtendDTO.ex_reviews, BookReviewExtendDTO.ex_user),
            )
            .where(
                and_(BookReviewExtendDTO.is_deleted == false(), BookReviewExtendDTO.is_draft == false())
            )  # draft is not target
            .order_by(BookReviewExtendDTO.last_modified_at)
            .limit(max_count)
        )
        book_with_reviews: list[BookWithReviewsAppModel] = []
        results = self._session.scalars(stmt).unique().all()
        for result in results:
            book_with_reviews.append(result.to_response())

        return BooksWithReviewsAppModel(book_with_reviews)

    def find_active_by_user_id(self, user_id: UUID) -> BooksWithReviewsAppModel:
        stmt = (
            select(BookExtendDTO)
            .join(BookReviewExtendDTO)
            .options(
                joinedload(BookExtendDTO.authors),
                joinedload(BookExtendDTO.publisher),
                joinedload(BookExtendDTO.tags),
                contains_eager(BookExtendDTO.ex_reviews, BookReviewExtendDTO.ex_user),
            )
            .where(
                and_(
                    BookReviewExtendDTO.user_id == user_id,
                    BookReviewExtendDTO.is_deleted == false(),
                    BookReviewExtendDTO.is_draft == false(),
                )
            )  # draft is not target
            .order_by(BookReviewExtendDTO.last_modified_at)
        )
        book_with_reviews: list[BookWithReviewsAppModel] = []
        results = self._session.scalars(stmt).unique().all()
        for result in results:
            book_with_reviews.append(result.to_response())

        return BooksWithReviewsAppModel(book_with_reviews)

    def find_by_user_id(self, user_id: UUID) -> BooksWithReviewsAppModel:
        stmt = (
            select(BookExtendDTO)
            .join(BookReviewExtendDTO)
            .options(
                joinedload(BookExtendDTO.authors),
                joinedload(BookExtendDTO.publisher),
                joinedload(BookExtendDTO.tags),
                contains_eager(BookExtendDTO.ex_reviews, BookReviewExtendDTO.ex_user),
            )
            .where(
                and_(
                    BookReviewExtendDTO.user_id == user_id,
                    BookReviewExtendDTO.is_deleted == false(),
                )
            )  # draft is target
            .order_by(BookReviewExtendDTO.last_modified_at)
        )
        book_with_reviews: list[BookWithReviewsAppModel] = []
        results = self._session.scalars(stmt).unique().all()
        for result in results:
            book_with_reviews.append(result.to_response())

        return BooksWithReviewsAppModel(book_with_reviews)
