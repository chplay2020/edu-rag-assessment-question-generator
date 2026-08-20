"""Merge heads

Revision ID: 5e94bc8d3427
Revises: 32cae1734f4e, b4e9a0c2d3f8
Create Date: 2026-08-20 07:01:34.916800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e94bc8d3427'
down_revision: Union[str, None] = ('32cae1734f4e', 'b4e9a0c2d3f8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
