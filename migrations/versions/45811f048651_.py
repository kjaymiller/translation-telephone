"""empty message

Revision ID: 45811f048651
Revises:
Create Date: 2022-07-06 13:09:41.156525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45811f048651'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rounds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('endmessage', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('translations', sa.JSON(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('views', sa.SmallInteger(), nullable=True),
    sa.Column('usergen', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rounds')
    # ### end Alembic commands ###
