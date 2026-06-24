"""05_add_publisher_catalog_cache

Revision ID: 31ac44f40d0f
Revises: 8b6f0c3d0d4f
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "31ac44f40d0f"
down_revision: Union[str, None] = "8b6f0c3d0d4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "publisher_catalog_cache",
        sa.Column("source_key", sa.String(length=100), nullable=False, comment="取得元キー"),
        sa.Column("payload_json", sa.UnicodeText(), nullable=False, comment="カタログJSON"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, comment="取得日時"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, comment="期限日時"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_modified", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("source_key"),
        comment="出版社カタログキャッシュ",
    )
    op.create_index(op.f("ix_publisher_catalog_cache_expires_at"), "publisher_catalog_cache", ["expires_at"], unique=False)
    op.create_index(op.f("ix_publisher_catalog_cache_is_deleted"), "publisher_catalog_cache", ["is_deleted"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_publisher_catalog_cache_is_deleted"), table_name="publisher_catalog_cache")
    op.drop_index(op.f("ix_publisher_catalog_cache_expires_at"), table_name="publisher_catalog_cache")
    op.drop_table("publisher_catalog_cache")
