"""thêm cột is_deleted và updated_at cho courses

Revision ID: bf4070a273b0
Revises: 218df56e48bc
Create Date: 2026-07-08 09:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Định danh revision, được sử dụng bởi Alembic.
revision: str = 'bf4070a273b0'
down_revision: Union[str, None] = '218df56e48bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('courses', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('courses', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    op.drop_column('courses', 'is_deleted')
    op.drop_column('courses', 'updated_at')
