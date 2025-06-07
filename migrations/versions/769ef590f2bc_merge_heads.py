"""merge heads

Revision ID: 769ef590f2bc
Revises: rename_problem_id_to_target_id
Create Date: 2025-06-06 21:17:45.956915

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "769ef590f2bc"
down_revision = "rename_problem_id_to_target_id"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
