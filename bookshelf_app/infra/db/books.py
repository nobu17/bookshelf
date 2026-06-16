from datetime import date
from typing import Self
from uuid import UUID

from sqlalchemy import Column, Date, ForeignKey, String, Table, Unicode, Uuid, delete, false, func, insert, or_, select
from sqlalchemy.orm import Mapped, Session, joinedload, mapped_column, relationship

from bookshelf_app.api.books.domain import (
    ISBN13,
    Author,
    Authors,
    Book,
    BookImageUrl,
    BookTitle,
    IBookRepository,
    Publisher,
    Tags,
)
from bookshelf_app.infra.db.database import Base

from .tags import TagDTO
from .reviews import BookReviewDTO

# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
books_publishers_association_table = Table(
    "books_publishers_association_table",
    Base.metadata,
    Column("books_book_id", ForeignKey("books.book_id")),
    Column("publishers_name", ForeignKey("publishers.name")),
)

books_authors_association_table = Table(
    "books_authors_association_table",
    Base.metadata,
    Column("books_book_id", ForeignKey("books.book_id")),
    Column("authors_name", ForeignKey("authors.name")),
)

books_tags_association_table = Table(
    "books_tags_association_table",
    Base.metadata,
    Column("books_book_id", ForeignKey("books.book_id")),
    Column("tags_tag_id", ForeignKey("tags.tag_id")),
)


# pylint: disable=unsubscriptable-object
class PublisherDTO(Base):
    __tablename__ = "publishers"
    __table_args__ = {"comment": "出版社"}

    name: Mapped[str] = mapped_column(Unicode(length=100), primary_key=True, comment="名称")

    def to_domain_model(self) -> Publisher:
        return Publisher(self.name)

    @classmethod
    def from_domain_model(cls, domain: Publisher) -> Self:
        model = cls()
        model.name = domain.get_value()
        return model


# pylint: disable=unsubscriptable-object
class AuthorDTO(Base):
    __tablename__ = "authors"
    __table_args__ = {"comment": "著者"}

    name: Mapped[str] = mapped_column(Unicode(length=100), primary_key=True, comment="著者")

    def to_domain_model(self) -> Author:
        return Author(self.name)

    @classmethod
    def from_domain_model(cls, domain: Author) -> Self:
        model = cls()
        model.name = domain.get_value()
        return model

    @classmethod
    def from_domain_models(cls, domains: Authors) -> list[Self]:
        lists = []
        for author in domains.get_values():
            model = cls()
            model.name = author.get_value()
            lists.append(model)

        return lists


# pylint: disable=unsubscriptable-object
class BookDTO(Base):
    __tablename__ = "books"
    __table_args__ = {"comment": "書籍情報"}

    book_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, comment="主キー")
    isbn13: Mapped[str] = mapped_column(String(length=13), nullable=False, index=True, comment="ISBN13")
    title: Mapped[str] = mapped_column(Unicode(length=100), nullable=False, index=True, comment="書籍名")
    image_url: Mapped[str] = mapped_column(String(length=1000), nullable=False, default="", comment="書影URL")
    published_at: Mapped[date] = mapped_column(Date, nullable=False, index=True, comment="出版日時")
    publisher: Mapped[PublisherDTO] = relationship(secondary=books_publishers_association_table)
    authors: Mapped[list[AuthorDTO]] = relationship(secondary=books_authors_association_table)
    tags: Mapped[list[TagDTO]] = relationship(secondary=books_tags_association_table)

    def to_domain_model(self) -> Book:
        isbn13 = ISBN13(self.isbn13)
        title = BookTitle(self.title)
        publisher = self.publisher.to_domain_model()
        authors = Authors([auth.to_domain_model() for auth in self.authors])
        tags = Tags([tag.to_domain_model() for tag in self.filter_deleted_tags()])

        return Book.create_for_orm(
            self.book_id, isbn13, title, publisher, authors, self.published_at, tags, BookImageUrl(self.image_url)
        )

    def filter_deleted_tags(self) -> list[TagDTO]:
        tags_filtered = []
        for tag in self.tags:
            if not tag.is_deleted:
                tags_filtered.append(tag)

        return tags_filtered

    @classmethod
    def from_domain_model_as_create(cls, domain: Book) -> Self:
        model = cls()
        model.book_id = domain.book_id
        model.isbn13 = domain.isbn13.value
        model.title = domain.title.get_value()
        model.image_url = domain.image_url.get_value()
        model.published_at = domain.published_at
        model.publisher = PublisherDTO.from_domain_model(domain.publisher)
        model.authors = AuthorDTO.from_domain_models(domain.authors)
        model.tags = []  # every time empty. when create as new
        return model


class SqlBookRepository(IBookRepository):
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def search_masters(self, keyword: str, max_count: int) -> list[tuple[Book, int]]:
        book_ids_stmt = (
            select(BookDTO.book_id)
            .join(BookDTO.publisher)
            .outerjoin(BookDTO.authors)
            .group_by(BookDTO.book_id, BookDTO.title)
            .order_by(BookDTO.title)
            .limit(max_count)
        )
        if keyword:
            like_keyword = f"%{keyword}%"
            book_ids_stmt = book_ids_stmt.where(
                or_(
                    BookDTO.title.ilike(like_keyword),
                    BookDTO.isbn13.ilike(like_keyword),
                    PublisherDTO.name.ilike(like_keyword),
                    AuthorDTO.name.ilike(like_keyword),
                )
            )

        book_ids = list(self._session.scalars(book_ids_stmt).all())
        if not book_ids:
            return []

        review_counts = (
            select(BookReviewDTO.book_id, func.count(BookReviewDTO.review_id).label("review_count"))
            .where(BookReviewDTO.is_deleted == false())
            .where(BookReviewDTO.book_id.in_(book_ids))
            .group_by(BookReviewDTO.book_id)
            .subquery()
        )
        stmt = (
            select(BookDTO, func.coalesce(review_counts.c.review_count, 0))
            .outerjoin(review_counts, BookDTO.book_id == review_counts.c.book_id)
            .where(BookDTO.book_id.in_(book_ids))
            .options(joinedload(BookDTO.authors), joinedload(BookDTO.publisher), joinedload(BookDTO.tags))
            .order_by(BookDTO.title)
        )
        results = self._session.execute(stmt).unique().all()
        return [(book.to_domain_model(), review_count) for book, review_count in results]

    def find_by_isbn13(self, isbn13: ISBN13) -> list[Book]:
        stmt = (
            select(BookDTO)
            .where(BookDTO.isbn13 == isbn13.value)
            .options(joinedload(BookDTO.authors), joinedload(BookDTO.publisher), joinedload(BookDTO.tags))
        )
        results = self._session.scalars(stmt).unique().all()
        return [result.to_domain_model() for result in results]

    def find_by_id(self, id: UUID) -> Book | None:
        stmt = (
            select(BookDTO)
            .where(BookDTO.book_id == id)
            .options(joinedload(BookDTO.authors), joinedload(BookDTO.publisher), joinedload(BookDTO.tags))
        )
        result = self._session.scalars(stmt).first()
        if result is None:
            return None

        return result.to_domain_model()

    def create(self, item: Book) -> Book:
        try:
            add_dto = BookDTO.from_domain_model_as_create(item)
            self._reuse_existing_master_relations(add_dto)

            self._session.add(add_dto)
            self._session.commit()
            self._session.refresh(add_dto)
            return item
        except Exception:
            self._session.rollback()
            raise

    def update(self, item: Book) -> Book:
        try:
            stmt = (
                select(BookDTO)
                .where(BookDTO.book_id == item.book_id)
                .options(joinedload(BookDTO.authors), joinedload(BookDTO.publisher), joinedload(BookDTO.tags))
            )
            book = self._session.scalars(stmt).first()
            if book is None:
                raise ValueError(f"book is not found. id:{item.book_id}")

            book.isbn13 = item.isbn13.value
            book.title = item.title.get_value()
            book.image_url = item.image_url.get_value()
            book.published_at = item.published_at
            book.publisher = self._resolve_publisher(PublisherDTO.from_domain_model(item.publisher))
            book.authors = self._resolve_authors(AuthorDTO.from_domain_models(item.authors))

            self._session.commit()
            self._session.refresh(book)
            return book.to_domain_model()
        except Exception:
            self._session.rollback()
            raise

    def update_tags(self, id: UUID, tag_ids: list[UUID]) -> None:
        try:
            stmt = select(BookDTO).where(BookDTO.book_id == id).options(joinedload(BookDTO.tags))
            book = self._session.scalars(stmt).first()
            if book is None:
                raise ValueError(f"book is not found. id:{id}")

            # deleting current relations
            if len(book.tags) > 0:
                stmt_delete = delete(books_tags_association_table).where(
                    books_tags_association_table.c.books_book_id == book.book_id
                )
                self._session.execute(stmt_delete)

            if len(tag_ids) > 0:
                stmt_insert = insert(books_tags_association_table).values(
                    [{"books_book_id": book.book_id, "tags_tag_id": tag_id} for tag_id in tag_ids]
                )
                self._session.execute(stmt_insert)

            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def delete(self, id: UUID) -> None:
        raise NotImplementedError()

    def _reuse_existing_master_relations(self, book: BookDTO) -> None:
        book.publisher = self._resolve_publisher(book.publisher)
        book.authors = self._resolve_authors(book.authors)

    def _resolve_publisher(self, original: PublisherDTO) -> PublisherDTO:
        select_pub_stmt = select(PublisherDTO).where(PublisherDTO.name == original.name)
        publisher = self._session.scalars(select_pub_stmt).first()
        if publisher is not None:
            return publisher

        self._session.add(original)
        self._session.flush([original])
        return original

    def _resolve_authors(self, originals: list[AuthorDTO]) -> list[AuthorDTO]:
        authors = self._session.query(AuthorDTO).filter(AuthorDTO.name.in_([x.name for x in originals])).all()
        for original in originals:
            matched = next((author for author in authors if author.name == original.name), None)
            if matched is None:
                self._session.add(original)
                self._session.flush([original])
                authors.append(original)
        return authors
