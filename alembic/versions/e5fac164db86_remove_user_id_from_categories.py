"""Remove user_id from categories

Revision ID: e5fac164db86
Revises:
Create Date: 2025-11-24 15:13:19.115036

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e5fac164db86"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
