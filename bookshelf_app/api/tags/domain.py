import abc
import uuid
from typing import Self

from bookshelf_app.api.shared.errors import DomainValidationError


class Tag:
    tag_id: uuid.UUID
    name: str

    def __init__(self, name: str):
        self.name = name
        self.tag_id = uuid.uuid4()
        self._validate()

    @classmethod
    def create_for_orm(cls, tag_id: uuid.UUID, name: str) -> Self:
        instance = cls(name)
        instance.tag_id = tag_id
        return instance

    def _validate(self):
        if not self.name:
            raise DomainValidationError(self.__class__.__name__, "name is empty")
        if len(self.name) > 15:
            raise DomainValidationError(self.__class__.__name__, "name length should be less than 16")

    def is_same_name(self, tag: Self) -> bool:
        return self.name == tag.name

    def is_same(self, tag: Self) -> bool:
        return self.tag_id == tag.tag_id

    def update_name(self, name: str):
        self.name = name
        self._validate()


class ITagRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fetch_all(self) -> list[Tag]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_name(self, name: str) -> Tag | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, id: uuid.UUID) -> Tag | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_ids(self, ids: list[uuid.UUID]) -> list[Tag]:
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, item: Tag) -> Tag:
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, item: Tag) -> Tag:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError()


class TagDomainService:
    _repos: ITagRepository

    def __init__(self, repos: ITagRepository):
        self._repos = repos

    def same_name_exists(self, item_to_check: Tag) -> bool:
        same_name = self._repos.find_by_name(item_to_check.name)
        if not same_name:
            return False
        # self is not checked
        if item_to_check.is_same(same_name):
            return False

        return True
