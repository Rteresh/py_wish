"""Initial delete releation active-wish-time-expire

Revision ID: 354e6231be6c
Revises: 50bfc6a61ae8
Create Date: 2024-04-03 21:58:52.940227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '354e6231be6c'
down_revision: Union[str, None] = '50bfc6a61ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('active_wishes', sa.Column('expired_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('active_wishes', 'expired_at')
    # ### end Alembic commands ###