"""empty message

Revision ID: 297c5bafc64c
Revises: 19aae46488dc
Create Date: 2018-11-08 21:54:31.297215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '297c5bafc64c'
down_revision = '19aae46488dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(length=30), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('date', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_author'), 'note', ['author'], unique=False)
    op.create_index(op.f('ix_note_date'), 'note', ['date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_note_date'), table_name='note')
    op.drop_index(op.f('ix_note_author'), table_name='note')
    op.drop_table('note')
    # ### end Alembic commands ###
