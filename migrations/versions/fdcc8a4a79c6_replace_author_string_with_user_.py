"""replace author string with user relationship in problem model

Revision ID: fdcc8a4a79c6
Revises: 8616d13977c5
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdcc8a4a79c6'
down_revision = '8616d13977c5'
branch_labels = None
depends_on = None


def upgrade():
    # Add author_id column as nullable first
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_problem_author', 'users', ['author_id'], ['id'])

    # Update existing problems to use a default user (assuming user with ID 1 exists)
    op.execute("UPDATE problems SET author_id = 1 WHERE author_id IS NULL")

    # Make author_id non-nullable
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.alter_column('author_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('author')


def downgrade():
    # Add back the author column
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.String(length=100), nullable=True))

    # Copy author names from users table
    op.execute("""
        UPDATE problems p 
        JOIN users u ON p.author_id = u.id 
        SET p.author = u.username
    """)

    # Make author non-nullable
    with op.batch_alter_table('problems', schema=None) as batch_op:
        batch_op.alter_column('author', nullable=False)
        batch_op.drop_constraint('fk_problem_author', type_='foreignkey')
        batch_op.drop_column('author_id')
