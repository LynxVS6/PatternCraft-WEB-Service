"""merge heads

Revision ID: cfa7794b46f9
Revises: add_discourse_tables, d89ad90b7b7a
Create Date: 2025-05-26 00:59:21.311435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfa7794b46f9'
down_revision = ('add_discourse_tables', 'd89ad90b7b7a')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
