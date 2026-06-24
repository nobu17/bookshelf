"""06_add_book_metadata_cache

Revision ID: 6e3b84f87db1
Revises: 31ac44f40d0f
Create Date: 2026-06-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6e3b84f87db1"
down_revision: Union[str, None] = "31ac44f40d0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "book_metadata_cache",
        sa.Column("isbn13", sa.String(length=13), nullable=False, comment="ISBN13"),
        sa.Column("payload_json", sa.UnicodeText(), nullable=False, comment="書籍メタデータJSON"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, comment="取得日時"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, comment="期限日時"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_modified", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("isbn13"),
        comment="書籍メタデータキャッシュ",
    )
    op.create_index(op.f("ix_book_metadata_cache_expires_at"), "book_metadata_cache", ["expires_at"], unique=False)
    op.create_index(op.f("ix_book_metadata_cache_is_deleted"), "book_metadata_cache", ["is_deleted"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_book_metadata_cache_is_deleted"), table_name="book_metadata_cache")
    op.drop_index(op.f("ix_book_metadata_cache_expires_at"), table_name="book_metadata_cache")
    op.drop_table("book_metadata_cache")
