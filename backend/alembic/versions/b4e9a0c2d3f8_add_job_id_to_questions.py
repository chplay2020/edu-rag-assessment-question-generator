"""add job_id to questions

Revision ID: b4e9a0c2d3f8
Revises: a3f8c91d2e47
Create Date: 2026-08-20 08:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b4e9a0c2d3f8'
down_revision: Union[str, None] = 'a3f8c91d2e47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('questions', sa.Column('job_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'questions', 'jobs', ['job_id'], ['id'], ondelete='CASCADE')

def downgrade() -> None:
    op.drop_constraint(None, 'questions', type_='foreignkey')
    op.drop_column('questions', 'job_id')
