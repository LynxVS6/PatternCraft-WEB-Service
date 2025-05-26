"""update bookmark_count default value

Revision ID: daa377546aa9
Revises: rename_satisfaction_to_bookmark
Create Date: 2025-05-26 11:16:27.065530

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'daa377546aa9'
down_revision = 'rename_satisfaction_to_bookmark'
branch_labels = None
depends_on = None


def upgrade():
    # First update any NULL values to 0
    op.execute('UPDATE problems SET bookmark_count = 0 WHERE bookmark_count IS NULL')
    
    # Then make the column NOT NULL
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.alter_column('bookmark_count',
                            existing_type=sa.Integer(),
                            nullable=False,
                            existing_server_default=sa.text('0'))


def downgrade():
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.alter_column('bookmark_count',
                            existing_type=sa.Integer(),
                            nullable=True,
                            existing_server_default=sa.text('0'))
