"""empty message

Revision ID: 254f289ff691
Revises: da64e6da27d5
Create Date: 2016-04-25 20:20:43.315631

"""

# revision identifiers, used by Alembic.
revision = '254f289ff691'
down_revision = 'da64e6da27d5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alert', sa.Column('checking_interval', sa.Integer(), nullable=True))
    op.add_column('alert', sa.Column('label', sa.Unicode(), nullable=True))
    op.add_column('alert', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'alert', 'user', ['user_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'alert', type_='foreignkey')
    op.drop_column('alert', 'user_id')
    op.drop_column('alert', 'label')
    op.drop_column('alert', 'checking_interval')
    ### end Alembic commands ###
