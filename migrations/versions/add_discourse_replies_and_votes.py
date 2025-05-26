"""Add discourse replies and votes tables

Revision ID: add_discourse_replies_and_votes
Revises: cfa7794b46f9
Create Date: 2024-03-19 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_discourse_replies_and_votes'
down_revision = 'cfa7794b46f9'
branch_labels = None
depends_on = None


def upgrade():
    # Create discourse_replies table
    op.create_table(
        'discourse_replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['comment_id'], ['discourse_comments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create discourse_votes table
    op.create_table(
        'discourse_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['comment_id'], ['discourse_comments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create discourse_reply_votes table
    op.create_table(
        'discourse_reply_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reply_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['reply_id'], ['discourse_replies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('discourse_reply_votes')
    op.drop_table('discourse_votes')
    op.drop_table('discourse_replies') 