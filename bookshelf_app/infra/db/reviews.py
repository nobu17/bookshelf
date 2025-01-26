from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.sql.expression import false

from bookshelf_app.api.reviews.domain import (
    BookReview,
    BookReviews,
    IBookReviewRepository,
    ReviewContent,
    ReviewDetail,
    ReviewState,
    ReviewStateEnum,
)
from bookshelf_app.infra.db.database import Base


# pylint: disable=unsubscriptable-object
class BookReviewDTO(Base):
    __tablename__ = "book_reviews"
    __table_args__ = {"comment": "書籍レビュー"}

    review_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, comment="主キー")
    content: Mapped[str] = mapped_column(String(length=10000), comment="レビュー本文")
    is_draft: Mapped[bool] = mapped_column(Boolean, comment="ドラフト")
    state: Mapped[ReviewStateEnum] = mapped_column(comment="状態", default=ReviewStateEnum.NOT_YET)
    last_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="最終更新日時")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="読了日")
    book_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("books.book_id"))
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.user_id"))

    def to_domain_model(self) -> BookReview:
        state = ReviewState.create_from_orm(self.state, self.completed_at, self.last_modified_at)
        content = ReviewContent.create_from_orm(self.content, self.is_draft)
        detail = ReviewDetail.create_from_orm(self.review_id, state, content)
        return BookReview.create_from_orm(detail, self.user_id, self.book_id)

    @classmethod
    def from_domain_model(cls, domain: BookReview) -> Self:
        model = cls()
        model.review_id = domain.detail.review_id
        model.content = domain.detail.content.get_value()
        model.is_draft = domain.detail.content.is_draft
        model.state = domain.detail.state.state
        model.last_modified_at = domain.detail.state.last_modified_at
        model.completed_at = domain.detail.state.completed_at
        model.book_id = domain.book_id
        model.user_id = domain.user_id

        return model


class SqlBookReviewRepository(IBookReviewRepository):
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def find_by_review_id(self, id: UUID) -> BookReview | None:
        stmt = select(BookReviewDTO).where(BookReviewDTO.review_id == id).where(BookReviewDTO.is_deleted == false())
        result = self._session.scalars(stmt).first()
        if result is None:
            return None

        return result.to_domain_model()

    def find_by_user_id(self, id: UUID) -> BookReviews:
        stmt = select(BookReviewDTO).where(BookReviewDTO.user_id == id).where(BookReviewDTO.is_deleted == false())
        results = self._session.scalars(stmt).all()

        return BookReviews.create_from_orm([res.to_domain_model() for res in results])

    def create(self, review: BookReview) -> BookReview:
        add_dto = BookReviewDTO.from_domain_model(review)
        self._session.add(add_dto)
        self._session.commit()
        self._session.refresh(add_dto)
        return add_dto.to_domain_model()

    def update(self, review: BookReview) -> BookReview:
        update_dto = BookReviewDTO.from_domain_model(review)
        stmt = (
            update(BookReviewDTO)
            .where(BookReviewDTO.review_id == review.detail.review_id)
            .values(
                content=update_dto.content,
                is_draft=update_dto.is_draft,
                state=update_dto.state,
                last_modified_at=update_dto.last_modified_at,
                completed_at=update_dto.completed_at,
            )
        )
        self._session.execute(stmt)
        self._session.commit()
        return update_dto.to_domain_model()

    def delete(self, id: UUID) -> None:
        stmt = update(BookReviewDTO).where(BookReviewDTO.review_id == id).values(is_deleted=True)
        self._session.execute(stmt)
        self._session.commit()
