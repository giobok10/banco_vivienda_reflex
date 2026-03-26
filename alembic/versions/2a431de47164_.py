"""empty message

Revision ID: 2a431de47164
Revises: 
Create Date: 2026-03-25 13:42:49.018499

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '2a431de47164'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initial baseline migration (no-op for existing Neon schema)."""
    return


def downgrade() -> None:
    """No-op downgrade for baseline migration."""
    return
