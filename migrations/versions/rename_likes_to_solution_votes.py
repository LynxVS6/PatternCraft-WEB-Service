"""rename likes to solution_votes

Revision ID: rename_likes_to_solution_votes
Revises: 468bab4e8eab
Create Date: 2024-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "rename_likes_to_solution_votes"
down_revision = "468bab4e8eab"
branch_labels = None
depends_on = None


def upgrade():
    # First, drop any foreign key constraints that might be using the unique index
    with op.batch_alter_table("likes") as batch_op:
        batch_op.drop_constraint("unique_user_solution_like", type_="unique")

    # Rename the table
    op.rename_table("likes", "solution_votes")

    # Add vote_type column
    op.add_column(
        "solution_votes",
        sa.Column("vote_type", sa.String(7), nullable=False, server_default="like"),
    )

    # Create new unique constraint with the new table name
    op.create_unique_constraint(
        "unique_user_solution_vote", "solution_votes", ["user_id", "target_id"]
    )


def downgrade():
    # Drop the new unique constraint
    with op.batch_alter_table("solution_votes") as batch_op:
        batch_op.drop_constraint("unique_user_solution_vote", type_="unique")

    # Drop the vote_type column
    op.drop_column("solution_votes", "vote_type")

    # Rename the table back
    op.rename_table("solution_votes", "likes")

    # Recreate the old unique constraint
    with op.batch_alter_table("likes") as batch_op:
        batch_op.create_unique_constraint(
            "unique_user_solution_like", ["user_id", "target_id"]
        )
