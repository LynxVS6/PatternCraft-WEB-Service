"""rename problem_id to target_id

Revision ID: rename_problem_id_to_target_id
Revises: rename_comment_id_to_target_id
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_problem_id_to_target_id'
down_revision = 'rename_comment_id_to_target_id'
branch_labels = None
depends_on = None


def upgrade():
    # Rename problem_id to target_id in problem_votes table
    op.alter_column('problem_votes', 'problem_id',
                    new_column_name='target_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False)


def downgrade():
    # Rename target_id back to problem_id in problem_votes table
    op.alter_column('problem_votes', 'target_id',
                    new_column_name='problem_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False) 