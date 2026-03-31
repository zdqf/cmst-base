"""add_user_password_hash

Revision ID: a1b2c3d4e5f6
Revises: 96586b7c8b97
Create Date: 2026-04-01 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '96586b7c8b97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('users', 'password_hash')
