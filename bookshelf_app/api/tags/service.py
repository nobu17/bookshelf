import uuid
from dataclasses import dataclass

from bookshelf_app.api.shared.errors import DataNotFoundError, DuplicateItemError
from bookshelf_app.api.tags.domain import ITagRepository, Tag, TagDomainService


@dataclass(frozen=True)
class TagBaseAppModel:
    name: str


@dataclass(frozen=True)
class TagCreateAppModel(TagBaseAppModel):
    pass


@dataclass(frozen=True)
class TagUpdateAppModel(TagBaseAppModel):
    pass


@dataclass(frozen=True)
class TagAppModel(TagBaseAppModel):
    tag_id: uuid.UUID


class TagService:
    ENTITY_NAME: str = "Tag"
    _repos: ITagRepository
    _domain_service: TagDomainService

    def __init__(self, repos: ITagRepository):
        self._repos = repos
        self._domain_service = TagDomainService(repos)

    def list(self) -> list[TagAppModel]:
        results: list[TagAppModel] = []

        tags = self._repos.fetch_all()
        for tag in tags:
            results.append(TagAppModel(**vars(tag)))

        return results

    def create(self, input: TagCreateAppModel) -> TagAppModel:
        tag = Tag(input.name)
        if self._domain_service.same_name_exists(tag):
            raise DuplicateItemError("Tag", "Name", tag.name)

        result = self._repos.create(tag)
        return TagAppModel(**vars(result))

    def update(self, id: uuid.UUID, input: TagUpdateAppModel) -> TagAppModel:
        current = self._repos.find_by_id(id)
        if not current:
            raise DataNotFoundError(str(id), self.ENTITY_NAME, "update")

        current.update_name(input.name)

        if self._domain_service.same_name_exists(current):
            raise DuplicateItemError("Tag", "Name", input.name)

        updated = self._repos.update(current)
        return TagAppModel(**vars(updated))

    def delete(self, id: uuid.UUID) -> None:
        current = self._repos.find_by_id(id)
        if not current:
            raise DataNotFoundError(str(id), self.ENTITY_NAME, "delete")

        self._repos.delete(id)

        return
