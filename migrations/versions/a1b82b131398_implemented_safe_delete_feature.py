"""implemented safe delete feature

Revision ID: a1b82b131398
Revises: b46679198350
Create Date: 2026-07-16 11:49:07.789742

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b82b131398'
down_revision: Union[str, Sequence[str], None] = 'b46679198350'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # === 1. FIX FOR BOOKS TABLE ===
    op.add_column('books', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('books', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE books SET is_deleted = FALSE")
    op.alter_column('books', 'is_deleted', nullable=False)
    op.create_index(op.f('ix_books_is_deleted'), 'books', ['is_deleted'], unique=False)

    # === 2. FIX FOR REVIEW TABLE ===
    # For timestamps, we use sa.func.now() to populate existing records with the current time
    op.add_column('review', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('review', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('review', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('review', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    op.execute("UPDATE review SET is_deleted = FALSE, created_at = NOW(), updated_at = NOW()")
    
    op.alter_column('review', 'is_deleted', nullable=False)
    op.alter_column('review', 'created_at', nullable=False)
    op.alter_column('review', 'updated_at', nullable=False)
    op.create_index(op.f('ix_review_is_deleted'), 'review', ['is_deleted'], unique=False)

    # === 3. FIX FOR USERS TABLE ===
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE users SET is_deleted = FALSE")
    op.alter_column('users', 'is_deleted', nullable=False)
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_is_deleted'), table_name='users')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'is_deleted')
    op.drop_index(op.f('ix_review_is_deleted'), table_name='review')
    op.drop_column('review', 'deleted_at')
    op.drop_column('review', 'is_deleted')
    op.drop_column('review', 'updated_at')
    op.drop_column('review', 'created_at')
    op.drop_index(op.f('ix_books_is_deleted'), table_name='books')
    op.drop_column('books', 'deleted_at')
    op.drop_column('books', 'is_deleted')