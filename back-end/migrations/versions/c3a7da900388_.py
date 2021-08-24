"""empty message

Revision ID: c3a7da900388
Revises: b70965f8d14d
Create Date: 2021-08-19 10:03:40.276634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3a7da900388'
down_revision = 'b70965f8d14d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daylyrecord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=32), nullable=True),
    sa.Column('total_assets', sa.Integer(), nullable=True),
    sa.Column('spare_assets', sa.Integer(), nullable=True),
    sa.Column('in_user_assets', sa.Integer(), nullable=True),
    sa.Column('discarded_assets', sa.Integer(), nullable=True),
    sa.Column('applications', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daylyrecord_date'), 'daylyrecord', ['date'], unique=False)
    op.create_index(op.f('ix_daylyrecord_id'), 'daylyrecord', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_daylyrecord_id'), table_name='daylyrecord')
    op.drop_index(op.f('ix_daylyrecord_date'), table_name='daylyrecord')
    op.drop_table('daylyrecord')
    # ### end Alembic commands ###