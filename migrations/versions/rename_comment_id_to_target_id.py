"""rename comment_id to target_id

Revision ID: rename_comment_id_to_target_id
Revises: a3cd275c47d7
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_comment_id_to_target_id'
down_revision = 'a3cd275c47d7'
branch_labels = None
depends_on = None


def upgrade():
    # Rename comment_id to target_id in comment_votes table
    op.alter_column('comment_votes', 'comment_id',
                    new_column_name='target_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False)


def downgrade():
    # Rename target_id back to comment_id in comment_votes table
    op.alter_column('comment_votes', 'target_id',
                    new_column_name='comment_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False) 