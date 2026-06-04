from datetime import date

import pytest

from bookshelf_app.api.book_search import service as target


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("2020", date(2020, 1, 1), id="year"),
        pytest.param("2020-02", date(2020, 2, 1), id="year month hyphen"),
        pytest.param("2020-02-03", date(2020, 2, 3), id="date hyphen"),
        pytest.param("202002", date(2020, 2, 1), id="year month compact"),
        pytest.param("20200203", date(2020, 2, 3), id="date compact"),
        pytest.param("", date(1970, 1, 1), id="empty"),
        pytest.param(None, date(1970, 1, 1), id="none"),
        pytest.param("unknown", date(1970, 1, 1), id="unknown"),
    ],
)
def test_parse_published_date(value: str | None, expected: date):
    assert target.parse_published_date(value) == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("4798121967", "9784798121963", id="valid isbn10"),
        pytest.param("invalid", None, id="invalid"),
    ],
)
def test_convert_isbn10_to_isbn13(value: str, expected: str | None):
    assert target.convert_isbn10_to_isbn13(value) == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("著者1、著者2/著者3", ["著者1", "著者2", "著者3"], id="separators"),
        pytest.param("", ["著者不明"], id="empty"),
    ],
)
def test_split_authors(value: str, expected: list[str]):
    assert target.split_authors(value) == expected
