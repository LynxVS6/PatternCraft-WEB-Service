"""Add created_at column to problems table

Revision ID: c43efcf906c1
Revises: e0d1e1624aed
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'c43efcf906c1'
down_revision = 'e0d1e1624aed'
branch_labels = None
depends_on = None

def upgrade():
    # First add the column as nullable
    op.add_column('problems', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Update existing records with current timestamp
    op.execute("UPDATE problems SET created_at = NOW() WHERE created_at IS NULL")
    
    # Make the column non-nullable
    op.alter_column('problems', 'created_at',
                    existing_type=sa.DateTime(),
                    nullable=False)

def downgrade():
    op.drop_column('problems', 'created_at')
