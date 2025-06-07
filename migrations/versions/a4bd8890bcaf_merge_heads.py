"""merge_heads

Revision ID: a4bd8890bcaf
Revises: rename_likes_to_solution_votes, rename_solution_id_to_target_id
Create Date: 2025-06-07 02:37:02.349233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4bd8890bcaf'
down_revision = ('rename_likes_to_solution_votes', 'rename_solution_id_to_target_id')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
