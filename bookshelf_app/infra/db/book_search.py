from datetime import datetime

from sqlalchemy import DateTime, String, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from bookshelf_app.infra.db.database import Base


class PublisherCatalogCacheDTO(Base):
    __tablename__ = "publisher_catalog_cache"
    __table_args__ = {"comment": "出版社カタログキャッシュ"}

    source_key: Mapped[str] = mapped_column(String(length=100), primary_key=True, comment="取得元キー")
    payload_json: Mapped[str] = mapped_column(UnicodeText, nullable=False, comment="カタログJSON")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="取得日時")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, comment="期限日時")


class BookMetadataCacheDTO(Base):
    __tablename__ = "book_metadata_cache"
    __table_args__ = {"comment": "書籍メタデータキャッシュ"}

    isbn13: Mapped[str] = mapped_column(String(length=13), primary_key=True, comment="ISBN13")
    payload_json: Mapped[str] = mapped_column(UnicodeText, nullable=False, comment="書籍メタデータJSON")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="取得日時")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, comment="期限日時")
