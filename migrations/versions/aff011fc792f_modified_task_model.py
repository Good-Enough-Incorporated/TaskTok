"""modified task model

Revision ID: aff011fc792f
Revises: 1520bdf7ab7a
Create Date: 2023-12-07 20:16:33.090767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aff011fc792f'
down_revision = '1520bdf7ab7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('taskreminder', schema=None) as batch_op:
        batch_op.add_column(sa.Column('task_is_recurring', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('task_archived', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('taskreminder', schema=None) as batch_op:
        batch_op.drop_column('task_archived')
        batch_op.drop_column('task_is_recurring')

    # ### end Alembic commands ###