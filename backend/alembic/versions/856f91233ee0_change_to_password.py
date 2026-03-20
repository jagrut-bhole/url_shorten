from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '856f91233ee0'
down_revision: Union[str, None] = 'c702fd0fb339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('password', sa.String(), nullable=False))
    op.drop_column('user', 'password_hash')


def downgrade() -> None:
    op.add_column('user', sa.Column('password_hash', sa.VARCHAR(), nullable=False))
    op.drop_column('user', 'password')