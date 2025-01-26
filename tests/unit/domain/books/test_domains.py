import pytest

from bookshelf_app.api.books.domain import Author, Authors, BookTitle, Publisher, Tags
from bookshelf_app.api.shared.errors import DomainValidationError
from bookshelf_app.api.tags.domain import Tag


# BookTitle
@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="white space"),
    ],
)
def test_book_title_error_empty(value: str):
    with pytest.raises(DomainValidationError) as e:
        BookTitle(value)

    assert str(e.value.detail) == "value is empty"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param(
            "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901",
            id="101 length",
        ),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890あ",
            id="101 length with full",
        ),
    ],
)
def test_book_title_error_over_limit(value: str):
    with pytest.raises(DomainValidationError) as e:
        BookTitle(value)

    assert str(e.value.detail) == "value length is over limit(100)"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("A", id="1 digits"),
        pytest.param("ABCDあ", id="multi digits"),
        pytest.param("AB C", id="contains white space"),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
            id="100 length",
        ),
    ],
)
def test_book_title_correct(value: str):
    title = BookTitle(value)

    assert title.get_value() == value


# Publisher
@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="white space"),
    ],
)
def test_publisher_error_empty(value: str):
    with pytest.raises(DomainValidationError) as e:
        Publisher(value)

    assert str(e.value.detail) == "value is empty"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param(
            "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901",
            id="101 length",
        ),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890あ",
            id="101 length with full",
        ),
    ],
)
def test_publisher_error_over_limit(value: str):
    with pytest.raises(DomainValidationError) as e:
        Publisher(value)

    assert str(e.value.detail) == "value length is over limit(100)"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("A", id="1 digits"),
        pytest.param("ABCDあ", id="multi digits"),
        pytest.param("AB C", id="contains white space"),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
            id="100 length",
        ),
    ],
)
def test_publisher_correct(value: str):
    title = Publisher(value)

    assert title.get_value() == value


# Author
@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="white space"),
    ],
)
def test_author_error_empty(value: str):
    with pytest.raises(DomainValidationError) as e:
        Author(value)

    assert str(e.value.detail) == "value is empty"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param(
            "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901",
            id="101 length",
        ),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890あ",
            id="101 length with full",
        ),
    ],
)
def test_author_error_over_limit(value: str):
    with pytest.raises(DomainValidationError) as e:
        Author(value)

    assert str(e.value.detail) == "value length is over limit(100)"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("A", id="1 digits"),
        pytest.param("ABCDあ", id="multi digits"),
        pytest.param("AB C", id="contains white space"),
        pytest.param(
            "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
            id="100 length",
        ),
    ],
)
def test_author_correct(value: str):
    title = Author(value)

    assert title.get_value() == value


# Authors
def test_authors_error_empty():
    with pytest.raises(DomainValidationError) as e:
        Authors([])

    assert str(e.value.detail) == "empty values"


@pytest.mark.parametrize(
    ["values"],
    [
        pytest.param(["A"], id="1 element"),
        pytest.param(["A", "BB", "CCC"], id="3 elements"),
    ],
)
def test_authors_correct(values: list[str]):
    val = [Author(x) for x in values]
    authors = Authors(val)

    actual = authors.get_values()
    assert len(actual) == len(values)

    index = 0
    for x in actual:
        assert x.get_value() == values[index]
        index += 1


# Tags
def test_tags_allow_empty():
    tags = Tags([])
    actual = tags.get_values()
    assert len(actual) == 0


@pytest.mark.parametrize(
    ["values"],
    [
        pytest.param(["A"], id="1 element"),
        pytest.param(["A", "BB", "CCC"], id="3 elements"),
    ],
)
def test_tags_correct(values: list[str]):
    val = [Tag(x) for x in values]
    tags = Tags(val)

    actual = tags.get_values()
    assert len(actual) == len(values)

    index = 0
    for x in actual:
        assert x.name == values[index]
        index += 1
