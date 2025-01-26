from typing import Self
from uuid import UUID

from sqlalchemy import JSON, String, Uuid, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.sql.expression import false

from bookshelf_app.api.auth.domain import (
    Email,
    IUserRepository,
    UserHashed,
    UserRoleEnum,
)

from .database import DeletableBase


class SqlUserRepository(IUserRepository):
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def find_by_email(self, email: Email) -> UserHashed | None:
        stmt = select(UserDTO).where(UserDTO.email == email.value).where(UserDTO.is_deleted == false())
        result = self._session.scalars(stmt).first()
        if result is None:
            return None

        return result.to_domain_model()

    def create(self, user: UserHashed) -> UserHashed:
        add_dto = UserDTO.from_domain_model(user)
        self._session.add(add_dto)
        self._session.commit()
        self._session.refresh(add_dto)
        return user


# pylint: disable=unsubscriptable-object
class UserDTO(DeletableBase):
    __tablename__ = "users"
    __table_args__ = {"comment": "ユーザー"}

    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, comment="主キー")
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, comment="ユーザー名")
    email: Mapped[str] = mapped_column(String(length=100), nullable=False, comment="メールアドレス")
    hashed_password: Mapped[str] = mapped_column(String(length=256), nullable=False, comment="パスワード")
    roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="ロール")

    def to_domain_model(self) -> UserHashed:
        roles = [UserRoleEnum(x) for x in self.roles]
        domain = UserHashed(self.name, self.email, roles, self.hashed_password)
        domain.user_id = self.user_id
        return domain

    @classmethod
    def from_domain_model(cls, domain: UserHashed) -> Self:
        model = cls()
        model.user_id = domain.user_id
        model.name = domain.name.value
        model.email = domain.email.value
        model.hashed_password = domain.hashed_password.value
        model.roles = [str(x) for x in domain.roles]
        return model
