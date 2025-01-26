import copy
from typing import Dict

from bookshelf_app.api.auth.domain import (
    Email,
    IUserRepository,
    Password,
    UserHashed,
    UserRoleEnum,
)
from bookshelf_app.infra.other.crypt import CryptService

crypt: CryptService = CryptService()


def create_default() -> Dict[str, UserHashed]:
    data = dict()

    # admin
    password1 = Password("Hoge123456789")
    user = UserHashed(
        name="admin",
        email="hoge@hoge.com",
        roles=[UserRoleEnum.Admin],
        hashed_password=crypt.create_hash(password1),
    )
    data[user.email.value] = user

    # normal
    password2 = Password("ABCabc12345")
    user = UserHashed(name="user", email="user@user.com", roles=[], hashed_password=crypt.create_hash(password2))
    data[user.email.value] = user

    return data


class MemoryUserRepository(IUserRepository):
    _data: Dict[str, UserHashed] = create_default()

    def __init__(self):
        pass

    def find_by_email(self, email: Email) -> UserHashed | None:
        if email.value not in MemoryUserRepository._data:
            return None
        return copy.deepcopy(MemoryUserRepository._data[email.value])

    def create(self, user: UserHashed) -> UserHashed:
        MemoryUserRepository._data[user.email.value] = user
        return copy.deepcopy(user)

    def clear(self):
        MemoryUserRepository._data = None


def clear_users() -> None:
    MemoryUserRepository().clear()
