"""empty message

Revision ID: 52aa596d0bbe
Revises: b4d0fe0d9176
Create Date: 2021-07-06 15:39:14.380142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52aa596d0bbe'
down_revision = 'b4d0fe0d9176'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'tags')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('tags', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###