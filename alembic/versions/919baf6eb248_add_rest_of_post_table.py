"""add rest of post table

Revision ID: 919baf6eb248
Revises: ad4397beeda4
Create Date: 2024-01-26 17:40:55.861639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '919baf6eb248'
down_revision: Union[str, None] = 'ad4397beeda4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column('rating', sa.Integer()))
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'rating')
    op.drop_column('posts', 'created_at')
    pass
