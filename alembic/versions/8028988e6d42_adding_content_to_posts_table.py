"""Adding content to posts table

Revision ID: 8028988e6d42
Revises: 8f6b9acb0110
Create Date: 2024-01-26 17:15:19.675785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8028988e6d42'
down_revision: Union[str, None] = '8f6b9acb0110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
