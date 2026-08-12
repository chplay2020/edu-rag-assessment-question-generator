"""add source_chunk_ids to questions

Revision ID: 9c1a6f2d4e8b
Revises: bf4070a273b0
Create Date: 2026-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c1a6f2d4e8b"
down_revision: Union[str, None] = "bf4070a273b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("source_chunk_ids", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("questions", "source_chunk_ids")
