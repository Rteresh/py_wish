"""Initial delete releation active-wish

Revision ID: 50bfc6a61ae8
Revises: 68c05d092d03
Create Date: 2024-04-03 21:34:56.130044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50bfc6a61ae8'
down_revision: Union[str, None] = '68c05d092d03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('active_wishes', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('active_wishes', 'created_at')
    # ### end Alembic commands ###
