from bookshelf_app.api.shared.errors import DomainValidationError


class StringLimitValueObject:
    _max_len: int
    _value: str

    def __init__(self, max_len: int, value: str):
        self._max_len = max_len
        self._value = value
        self._validate()

    def _validate(self):
        if self._max_len < 1:
            raise DomainValidationError(
                self.__class__.__name__, f"invalid is max_length. need more than 0. value:{self._max_len}"
            )
        if not self._value.strip():
            raise DomainValidationError(self.__class__.__name__, "value is empty")
        if len(self._value) > self._max_len:
            raise DomainValidationError(self.__class__.__name__, f"value length is over limit({self._max_len})")

    def get_value(self) -> str:
        return self._value


class StringAllowEmptyLimitValueObject:
    _max_len: int
    _value: str

    def __init__(self, max_len: int, value: str):
        self._max_len = max_len
        self._value = value
        self._validate()

    def _validate(self):
        if len(self._value) > self._max_len:
            raise DomainValidationError(self.__class__.__name__, f"value length is over limit({self._max_len})")

    def get_value(self) -> str:
        return self._value
