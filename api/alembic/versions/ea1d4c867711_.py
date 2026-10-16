"""empty message

Revision ID: ea1d4c867711
Revises: 226664d29595
Create Date: 2026-10-16 16:50:46.911059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea1d4c867711'
down_revision: Union[str, Sequence[str], None] = '226664d29595'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
