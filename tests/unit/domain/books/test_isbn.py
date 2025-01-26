import pytest

from bookshelf_app.api.books.domain import ISBN13
from bookshelf_app.api.shared.errors import DomainValidationError


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield


def test_isbn_error_empty():
    with pytest.raises(DomainValidationError) as e:
        ISBN13("")

    # エラーメッセージを検証
    assert str(e.value.detail) == "value is empty"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("1", id="1 digit"),
        pytest.param("12", id="2 digit"),
        pytest.param("123", id="3 digit"),
        pytest.param("1234", id="4 digit"),
        pytest.param("12345", id="5 digit"),
        pytest.param("123456", id="6 digit"),
        pytest.param("1234567", id="7 digit"),
        pytest.param("12345678", id="8 digit"),
        pytest.param("123456789", id="9 digit"),
        pytest.param("1234567890", id="10 digit"),
        pytest.param("12345678901", id="11 digit"),
        pytest.param("123456789012", id="12 digit"),
        pytest.param("12345678901234", id="14 digit"),
    ],
)
def test_isbn_error_not_correct_length(value: str):
    with pytest.raises(DomainValidationError) as e:
        ISBN13(value)

    assert str(e.value.detail) == "value length should be 13"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("9711234567890", id="start with 971"),
        pytest.param("9181234567890", id="start with 918"),
        pytest.param("1781234567890", id="start with 178"),
        pytest.param("9771234567890", id="start with 977"),
    ],
)
def test_isbn_error_incorrect_prefix(value: str):
    with pytest.raises(DomainValidationError) as e:
        ISBN13(value)

    assert str(e.value.detail) == "value should be start with 978 or 979"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("978123456789a", id="end with alphabet"),
        pytest.param("97812345678a1", id="mix with a alphabet"),
        pytest.param("97812345b7a10", id="mix with alphabets"),
        pytest.param("979123456789０", id="mix with full case numeric"),
    ],
)
def test_isbn_error_not_numeric(value: str):
    with pytest.raises(DomainValidationError) as e:
        ISBN13(value)

    assert str(e.value.detail) == "value should be only numeric"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("9784296001861", id="correct is 6"),
    ],
)
def test_isbn_error_incorrect_check_digits(value: str):
    with pytest.raises(DomainValidationError) as e:
        ISBN13(value)

    assert str(e.value.detail) == "invalid check digits. actual:1, expected:6"


@pytest.mark.parametrize(
    ["value"],
    [
        pytest.param("9784296001866", id="correct about 978"),
        pytest.param("9794296001865", id="correct about 979"),
        pytest.param("9784814400690", id="check digits is 0"),
        pytest.param("9784814400041", id="check digits is 1"),
        pytest.param("9784814400072", id="check digits is 2"),
        pytest.param("9784814400683", id="check digits is 3"),
        pytest.param("9784814400164", id="check digits is 4"),
        pytest.param("9784814400195", id="check digits is 5"),
        pytest.param("9784814400676", id="check digits is 6"),
        pytest.param("9784814400287", id="check digits is 7"),
        pytest.param("9784814400348", id="check digits is 8"),
        pytest.param("9784814400669", id="check digits is 9"),
    ],
)
def test_isbn_correct(value: str):
    data = ISBN13(value)

    assert data.value == value
