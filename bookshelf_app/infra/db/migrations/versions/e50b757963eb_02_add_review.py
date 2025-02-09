"""02_add_review

Revision ID: e50b757963eb
Revises: 94dd2c378990
Create Date: 2025-01-04 18:36:29.415190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e50b757963eb'
down_revision: Union[str, None] = '94dd2c378990'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_reviews',
    sa.Column('review_id', sa.Uuid(), nullable=False, comment='主キー'),
    sa.Column('content', sa.String(length=10000), nullable=False, comment='レビュー本文'),
    sa.Column('is_draft', sa.Boolean(), nullable=False, comment='ドラフト'),
    sa.Column('state', sa.Enum('NOT_YET', 'IN_PROGRESS', 'COMPLETED', name='reviewstateenum'), nullable=False, comment='状態'),
    sa.Column('last_modified_at', sa.DateTime(timezone=True), nullable=False, comment='最終更新日時'),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='読了日'),
    sa.Column('book_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('review_id'),
    comment='書籍レビュー'
    )
    op.create_index(op.f('ix_book_reviews_is_deleted'), 'book_reviews', ['is_deleted'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_book_reviews_is_deleted'), table_name='book_reviews')
    op.drop_table('book_reviews')
    # ### end Alembic commands ###
