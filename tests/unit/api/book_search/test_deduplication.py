from datetime import date

from bookshelf_app.api.book_search import service as target
from tests.unit.api.book_search.helper import create_book


def test_unique_books_prefers_richer_duplicate_isbn():
    poor = create_book(
        isbn13="9784798121963",
        publisher="不明",
        authors=["著者不明"],
        image_url=None,
        description=None,
        published_at=date(1970, 1, 1),
    )
    rich = create_book(
        isbn13="9784798121963",
        publisher="翔泳社",
        authors=["エリックエヴァンス"],
        image_url="https://example.com/cover.jpg",
        description="description",
        published_at=date(2011, 4, 1),
    )

    actual = target.unique_books([poor, rich])

    assert actual == [rich]


def test_unique_books_treats_same_title_publisher_year_as_duplicate():
    pod = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
        description=None,
    )
    sales = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="翔泳社",
        isbn13="9784798131627",
        published_at=date(2015, 12, 1),
        description="richer",
    )

    actual = target.unique_books([pod, sales])

    assert actual == [sales]


def test_unique_books_keeps_same_title_publisher_when_year_is_different():
    first = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
    )
    second = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="翔泳社",
        isbn13="9784798131627",
        published_at=date(2016, 3, 1),
    )

    actual = target.unique_books([first, second])

    assert actual == [first, second]


def test_unique_books_keeps_same_title_year_when_publisher_is_different():
    first = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者A"],
        publisher="翔泳社",
        isbn13="9784798131610",
        published_at=date(2015, 3, 1),
    )
    second = create_book(
        title="実践ドメイン駆動設計",
        authors=["著者B"],
        publisher="別出版社",
        isbn13="9784798131627",
        published_at=date(2015, 3, 1),
    )

    actual = target.unique_books([first, second])

    assert actual == [first, second]


def test_unique_books_treats_normalized_title_and_author_as_duplicate():
    rich = create_book(
        title="「実践ドメイン駆動設計」から学ぶDDDの実装入門",
        authors=["WINGSプロジェクト 青木 淳夫"],
        publisher="翔泳社",
        isbn13="9784798161495",
        published_at=date(2019, 5, 31),
        description="richer",
    )
    poor = create_book(
        title="実践ドメイン駆動設計から学ぶDDDの実装入門",
        authors=["青木淳夫"],
        publisher="不明",
        isbn13="9784798161501",
        published_at=date(2019, 5, 31),
        description=None,
    )

    actual = target.unique_books([poor, rich])

    assert actual == [rich]
