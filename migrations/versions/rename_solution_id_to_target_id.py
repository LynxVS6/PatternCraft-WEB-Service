"""rename solution_id to target_id

Revision ID: rename_solution_id_to_target_id
Revises: 468bab4e8eab
Create Date: 2024-03-19 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_solution_id_to_target_id'
down_revision = '468bab4e8eab'  # This is the correct previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Rename the column from solution_id to target_id
    with op.batch_alter_table('solution_votes') as batch_op:
        batch_op.alter_column('solution_id',
                            new_column_name='target_id',
                            existing_type=sa.Integer(),
                            existing_nullable=False)


def downgrade():
    # Rename the column back from target_id to solution_id
    with op.batch_alter_table('solution_votes') as batch_op:
        batch_op.alter_column('target_id',
                            new_column_name='solution_id',
                            existing_type=sa.Integer(),
                            existing_nullable=False) 