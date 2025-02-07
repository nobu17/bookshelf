import uuid
from datetime import date, datetime

# temporary fix for tool
# below is the solution to fix this
# https://zenn.dev/hpp/articles/6307447e5a037d
import sys
sys.path.append(".")

from bookshelf_app.api.books.domain import (
    ISBN13,
    Author,
    Authors,
    Book,
    BookTitle,
    Publisher,
    Tags,
)
from bookshelf_app.api.reviews.domain import (
    BookReview,
    ReviewContent,
    ReviewDetail,
    ReviewState,
    ReviewStateEnum,
)
from bookshelf_app.api.tags.domain import Tag
from bookshelf_app.infra.db.books import SqlBookRepository
from bookshelf_app.infra.db.database import get_session, truncate_tables
from bookshelf_app.infra.db.reviews import SqlBookReviewRepository
from bookshelf_app.infra.db.tags import SqlTagRepository
from bookshelf_app.tools.seeds.user import create_initial_admin


def main():
    reset_and_create_initial()


def reset_and_create_initial():
    truncate_tables()
    create_test_initial_data_set()


def create_test_initial_data_set():
    admin = create_initial_admin()
    tags = create_test_tags()
    books = create_test_books(tags)
    create_test_reviews(books[0], books[1], admin.user_id)


def create_test_tags() -> list[Tag]:
    session_itr = get_session()
    repos = SqlTagRepository(session_itr.__next__())
    tag1 = Tag("Tag1")
    tag2 = Tag("Tag2")

    tags: list[Tag] = []
    tags.append(repos.create(tag1))
    tags.append(repos.create(tag2))

    return tags


def create_test_books(tag_list: list[Tag]) -> list[Book]:
    session_itr = get_session()
    repos = SqlBookRepository(session_itr.__next__())
    book1 = _create_book(
        "9784814400973",
        ["Maximiliano Contieri"],
        "クリーンコードクックブック",
        "オライリージャパン",
        date(2024, 12, 10),
        tag_list,
    )
    book2 = _create_book(
        "9784814401024",
        ["Ted Young", "Austin Parker"],
        "入門 OpenTelemetry",
        "オライリージャパン",
        date(2025, 1, 11),
        [tag_list[0]],
    )
    books: list[Book] = []
    books.append(repos.create(book1))
    books.append(repos.create(book2))

    return books


def create_test_reviews(book1: Book, book2: Book, user_id: uuid.UUID):
    session_itr = get_session()
    repos = SqlBookReviewRepository(session_itr.__next__())

    state1 = ReviewState()
    state1.update(ReviewStateEnum.COMPLETED, completed_at=datetime.now())
    content1 = ReviewContent("感想です。", True)
    detail1 = ReviewDetail(state1, content1)
    review1 = BookReview(user_id, book1.book_id, detail1)

    state2 = ReviewState()
    state2.update(ReviewStateEnum.COMPLETED, completed_at=datetime.now())
    content2 = ReviewContent("感想?。", True)
    detail2 = ReviewDetail(state2, content2)
    review2 = BookReview(user_id, book2.book_id, detail2)

    repos.create(review1)
    repos.create(review2)


def _create_book(isbn13: str, author_list: list[str], title: str, publisher: str, pub_at: date, tag_list: list[Tag]):
    isbn13_d = ISBN13(isbn13)
    authors = Authors([Author(x) for x in author_list])
    title_d = BookTitle(title)
    pub = Publisher(publisher)
    tags = Tags(tag_list)
    return Book(isbn13_d, title_d, pub, authors, pub_at, tags)


if __name__ == "__main__":
    main()
