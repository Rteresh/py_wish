"""Initial all database

Revision ID: d3f872fe9301
Revises: 87678b9f99be
Create Date: 2024-04-01 20:59:23.342671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f872fe9301'
down_revision: Union[str, None] = '87678b9f99be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user1_id', sa.Integer(), nullable=True),
    sa.Column('user2_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pairs_id'), 'pairs', ['id'], unique=False)
    op.create_table('wishes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('fulfilled_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wishes_description'), 'wishes', ['description'], unique=False)
    op.create_index(op.f('ix_wishes_id'), 'wishes', ['id'], unique=False)
    op.create_index(op.f('ix_wishes_title'), 'wishes', ['title'], unique=False)
    op.create_table('active_wishes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('executor_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('wish_id', sa.Integer(), nullable=True),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('fulfilled_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['executor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wish_id'], ['wishes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_active_wishes_id'), 'active_wishes', ['id'], unique=False)
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_matched', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_matched')
    op.drop_column('users', 'created_at')
    op.drop_index(op.f('ix_active_wishes_id'), table_name='active_wishes')
    op.drop_table('active_wishes')
    op.drop_index(op.f('ix_wishes_title'), table_name='wishes')
    op.drop_index(op.f('ix_wishes_id'), table_name='wishes')
    op.drop_index(op.f('ix_wishes_description'), table_name='wishes')
    op.drop_table('wishes')
    op.drop_index(op.f('ix_pairs_id'), table_name='pairs')
    op.drop_table('pairs')
    # ### end Alembic commands ###
