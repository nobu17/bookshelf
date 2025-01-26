import abc
import re
from enum import StrEnum, auto
from uuid import UUID, uuid4

from bookshelf_app.api.shared.errors import DomainValidationError


class Email:
    value: str

    def __init__(self, value: str):
        self.value = value
        self._validate()

    def _validate(self):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, self.value) is None:
            raise DomainValidationError(self.__class__.__name__, "email is invalid.")


class Password:
    value: str

    def __init__(self, value: str):
        self.value = value
        self._validate()

    def _validate(self):
        pattern = r"\A(?=.*?[a-z])(?=.*?[A-Z])(?=.*?\d)[a-zA-Z\d]{8,100}\Z"
        if re.match(pattern, self.value) is None:
            raise DomainValidationError(
                self.__class__.__name__, "password should be 8-100 length and have upper and lower and numeric"
            )


class UserName:
    value: str

    def __init__(self, value: str):
        self.value = value
        self._validate()

    def _validate(self):
        if len(self.value.strip()) < 1:
            raise DomainValidationError(self.__class__.__name__, "user name should be 1-20 length")
        if len(self.value) > 20:
            raise DomainValidationError(self.__class__.__name__, "user name should be 1-20 length")


class HashedPassword:
    value: str

    def __init__(self, value: str):
        self.value = value
        self._validate()

    def _validate(self):
        if len(self.value.strip()) < 1:
            raise DomainValidationError(self.__class__.__name__, "hashed password should not be empty")


class LoginRequest:
    email: Email
    password: Password

    def __init__(self, email: str, password: str):
        self.email = Email(email)
        self.password = Password(password)


class UserRoleEnum(StrEnum):
    Admin = auto()

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None


class UserBase:
    user_id: UUID
    name: UserName
    email: Email
    roles: list[UserRoleEnum]

    def __init__(self, name: str, email: str, roles: list[UserRoleEnum]):
        self.user_id = uuid4()
        self.name = UserName(name)
        self.email = Email(email)
        self.roles = roles


class UserHashed(UserBase):
    hashed_password: HashedPassword

    def __init__(self, name: str, email: str, roles: list[UserRoleEnum], hashed_password: str):
        super().__init__(name, email, roles)
        self.hashed_password = HashedPassword(hashed_password)


class IUserRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_by_email(self, email: Email) -> UserHashed | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, user: UserHashed) -> UserHashed:
        raise NotImplementedError()


class Token:
    access_token: str
    token_type: str

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.token_type = "bearer"


class DecodeTokenData:
    email: str

    def __init__(self, email: str):
        self.email = email


class ICryptService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_hash(self, password: Password) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def verify(self, plain_pass: Password, hashed_pass: HashedPassword) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_token(self, user: UserBase) -> Token:
        raise NotImplementedError()

    @abc.abstractmethod
    def decode_token(self, token: str) -> DecodeTokenData:
        raise NotImplementedError()
