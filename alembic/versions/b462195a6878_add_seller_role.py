"""add_seller_role

Revision ID: b462195a6878
Revises: 43979cc6b3f9
Create Date: 2026-05-19 08:11:43.981005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b462195a6878'
down_revision: Union[str, Sequence[str], None] = '43979cc6b3f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE role ADD VALUE IF NOT EXISTS 'seller'")


def downgrade() -> None:
    """Downgrade schema."""
    pass