"""Initial migration - create all tables

Revision ID: b58fd50c2ec2
Revises: 1ff2a12c2aa1
Create Date: 2025-12-27 23:22:01.900629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b58fd50c2ec2'
down_revision: Union[str, Sequence[str], None] = '1ff2a12c2aa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
