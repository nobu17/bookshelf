import copy
import uuid
from typing import Dict

from bookshelf_app.api.tags.domain import ITagRepository, Tag


class MemoryTagRepository(ITagRepository):
    _data: Dict[uuid.UUID, Tag] = dict()

    def __init__(self):
        pass

    def fetch_all(self) -> list[Tag]:
        return copy.deepcopy(list(MemoryTagRepository._data.values()))

    def find_by_name(self, name: str) -> Tag | None:
        same_names = list(filter(lambda key: self._data[key].name == name, self._data))
        if len(same_names) == 0:
            return None

        return copy.deepcopy(MemoryTagRepository._data[same_names[0]])

    def find_by_id(self, id: uuid.UUID) -> Tag | None:
        if id not in MemoryTagRepository._data:
            return None
        return copy.deepcopy(MemoryTagRepository._data[id])

    def find_by_ids(self, ids: list[uuid.UUID]) -> list[Tag]:
        lists = []
        for id in ids:
            data = self.find_by_id(id)
            if data is not None:
                lists.append(data)

        return lists

    def create(self, item: Tag) -> Tag:
        MemoryTagRepository._data[item.tag_id] = item
        return copy.deepcopy(item)

    def update(self, item: Tag) -> Tag:
        if item.tag_id not in MemoryTagRepository._data:
            raise ValueError("not exists.")
        MemoryTagRepository._data[item.tag_id] = item
        return copy.deepcopy(item)

    def delete(self, id: uuid.UUID) -> None:
        del self._data[id]
        return

    def clear(self) -> None:
        MemoryTagRepository._data = dict()
        return


def clear_tags() -> None:
    MemoryTagRepository().clear()
