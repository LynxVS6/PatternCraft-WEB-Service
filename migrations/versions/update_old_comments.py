"""Update old comments to match new structure

Revision ID: update_old_comments
Revises: a3cd275c47d7
Create Date: 2024-03-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_old_comments'
down_revision = 'a3cd275c47d7'
branch_labels = None
depends_on = None


def upgrade():
    # Add vote_count column to comments table
    op.add_column('comments', sa.Column('vote_count', sa.Integer(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('comments', 'vote_count') 