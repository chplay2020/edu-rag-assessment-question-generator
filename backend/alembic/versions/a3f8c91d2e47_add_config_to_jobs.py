"""thêm cột config vào bảng jobs

Revision ID: a3f8c91d2e47
Revises: 9c1a6f2d4e8b
Create Date: 2026-08-20 08:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a3f8c91d2e47'
down_revision: Union[str, None] = '9c1a6f2d4e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    from sqlalchemy.engine.reflection import Inspector
    inspector = Inspector.from_engine(conn)
    columns = [c['name'] for c in inspector.get_columns('jobs')]
    if 'config' not in columns:
        op.add_column('jobs', sa.Column('config', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('jobs', 'config')
