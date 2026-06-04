"""04_add_book_image_url

Revision ID: 8b6f0c3d0d4f
Revises: 1a473f7d1dd1
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b6f0c3d0d4f"
down_revision: Union[str, None] = "1a473f7d1dd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("books", sa.Column("image_url", sa.String(length=1000), nullable=False, server_default="", comment="書影URL"))
    op.alter_column("books", "image_url", server_default=None)


def downgrade() -> None:
    op.drop_column("books", "image_url")
