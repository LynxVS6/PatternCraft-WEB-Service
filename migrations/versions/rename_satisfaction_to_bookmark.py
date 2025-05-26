"""rename satisfaction to bookmark

Revision ID: rename_satisfaction_to_bookmark
Revises: 4f3a3bd4e802
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_satisfaction_to_bookmark'
down_revision = '4f3a3bd4e802'  # Points to fix_discourse_reply_relationship migration
branch_labels = None
depends_on = None


def upgrade():
    # Rename satisfaction_rating to bookmark_count
    op.alter_column('problems', 'satisfaction_rating',
                    new_column_name='bookmark_count',
                    type_=sa.Integer(),
                    existing_type=sa.Float(),
                    postgresql_using='satisfaction_rating::integer')

    # Create bookmarks table
    op.create_table('bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'problem_id', name='unique_user_problem_bookmark')
    )


def downgrade():
    # Drop bookmarks table
    op.drop_table('bookmarks')

    # Rename bookmark_count back to satisfaction_rating
    op.alter_column('problems', 'bookmark_count',
                    new_column_name='satisfaction_rating',
                    type_=sa.Float(),
                    existing_type=sa.Integer(),
                    postgresql_using='bookmark_count::float') 