"""fix_role_enum_creater_to_creator

Revision ID: 43979cc6b3f9
Revises: 2968871e6c28
Create Date: 2026-05-19 08:09:57.243415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43979cc6b3f9'
down_revision: Union[str, Sequence[str], None] = '2968871e6c28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE role RENAME VALUE 'creater' TO 'creator'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE role RENAME VALUE 'creator' TO 'creater'")
