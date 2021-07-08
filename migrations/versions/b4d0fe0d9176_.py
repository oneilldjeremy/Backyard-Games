"""empty message

Revision ID: b4d0fe0d9176
Revises: 3e367982c963
Create Date: 2021-07-02 12:15:52.517594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4d0fe0d9176'
down_revision = '3e367982c963'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag')
    )
    op.create_table('tag_game_xref',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'game_id')
    )
    op.drop_table('categories')
    op.add_column('games', sa.Column('tags', sa.String(), nullable=True))
    op.drop_constraint('games_category_id_fkey', 'games', type_='foreignkey')
    op.drop_column('games', 'category_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('games_category_id_fkey', 'games', 'categories', ['category_id'], ['id'])
    op.drop_column('games', 'tags')
    op.create_table('categories',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='categories_pkey')
    )
    op.drop_table('tag_game_xref')
    op.drop_table('tags')
    # ### end Alembic commands ###