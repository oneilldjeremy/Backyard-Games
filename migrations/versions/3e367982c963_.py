"""empty message

Revision ID: 3e367982c963
Revises: 
Create Date: 2021-06-30 14:51:46.667226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e367982c963'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplies', sa.Column('quantity', sa.Integer(), nullable=True))
    op.add_column('supplies', sa.Column('estimated_total_cost', sa.String(), nullable=True))
    op.add_column('supplies', sa.Column('game_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'supplies', 'games', ['game_id'], ['id'])
    op.drop_column('supplies', 'estimated_cost')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplies', sa.Column('estimated_cost', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'supplies', type_='foreignkey')
    op.drop_column('supplies', 'game_id')
    op.drop_column('supplies', 'estimated_total_cost')
    op.drop_column('supplies', 'quantity')
    # ### end Alembic commands ###