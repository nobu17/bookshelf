from typing import Self
from uuid import UUID

from sqlalchemy import String, Uuid, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.sql.expression import false

from bookshelf_app.api.tags.domain import ITagRepository, Tag
from bookshelf_app.infra.db.database import DeletableBase


# pylint: disable=unsubscriptable-object
class TagDTO(DeletableBase):
    __tablename__ = "tags"
    __table_args__ = {"comment": "タグ"}

    tag_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, comment="主キー")
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, index=True, comment="タグ名")

    def to_domain_model(self) -> Tag:
        return Tag.create_for_orm(self.tag_id, self.name)

    def update_from_domain_model(self, domain: Tag):
        self.name = domain.name

    @classmethod
    def from_domain_model(cls, domain: Tag) -> Self:
        model = cls()
        model.tag_id = domain.tag_id
        model.name = domain.name
        return model


class SqlTagRepository(ITagRepository):
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def fetch_all(self) -> list[Tag]:
        stmt = select(TagDTO).where(TagDTO.is_deleted == false())
        results = self._session.scalars(stmt).all()

        return [res.to_domain_model() for res in results]

    def find_by_name(self, name: str) -> Tag | None:
        stmt = select(TagDTO).where(TagDTO.name == name).where(TagDTO.is_deleted == false())
        result = self._session.scalars(stmt).first()
        if result is None:
            return None

        return result.to_domain_model()

    def find_by_id(self, id: UUID) -> Tag | None:
        stmt = select(TagDTO).where(TagDTO.tag_id == id).where(TagDTO.is_deleted == false())
        result = self._session.scalars(stmt).first()
        if result is None:
            return None

        return result.to_domain_model()

    def find_by_ids(self, ids: list[UUID]) -> list[Tag]:
        stmt = select(TagDTO).where(TagDTO.tag_id.in_(ids)).where(TagDTO.is_deleted == false())
        results = self._session.scalars(stmt).all()

        return [res.to_domain_model() for res in results]

    def create(self, item: Tag) -> Tag:
        add_dto = TagDTO.from_domain_model(item)
        self._session.add(add_dto)
        self._session.commit()
        self._session.refresh(add_dto)
        return item

    def update(self, item: Tag) -> Tag:
        stmt = update(TagDTO).where(TagDTO.tag_id == item.tag_id).values(name=item.name)
        self._session.execute(stmt)
        self._session.commit()

        return item

    def delete(self, id: UUID) -> None:
        stmt = update(TagDTO).where(TagDTO.tag_id == id).values(is_deleted=True)
        self._session.execute(stmt)
        self._session.commit()
