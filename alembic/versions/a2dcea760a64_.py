"""empty message

Revision ID: a2dcea760a64
Revises: 2a431de47164
Create Date: 2026-03-26 11:38:05.397998

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'a2dcea760a64'
down_revision: Union[str, Sequence[str], None] = '2a431de47164'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Schema alignment baseline (no-op)."""
    return


def downgrade() -> None:
    """No-op downgrade for schema alignment baseline."""
    return
