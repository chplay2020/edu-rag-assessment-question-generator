"""add_export_history_fields

Revision ID: 36291a7861a4
Revises: 5e94bc8d3427
Create Date: 2026-08-20 18:30:10.841335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36291a7861a4'
down_revision: Union[str, None] = '5e94bc8d3427'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('exports') as batch_op:
        batch_op.add_column(sa.Column('question_ids', sa.JSON(), server_default='[]', nullable=False))
        batch_op.alter_column('course_id', existing_type=sa.Integer(), nullable=True)
    
    with op.batch_alter_table('exports') as batch_op:
        batch_op.alter_column('question_ids', server_default=None)


def downgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT count(1) FROM exports WHERE course_id IS NULL"))
    count = result.scalar()
    
    if count and count > 0:
        raise Exception(f"Cannot downgrade: Found {count} records in 'exports' with course_id IS NULL. Please assign a course_id to these records or delete them manually before downgrading.")
        
    with op.batch_alter_table('exports') as batch_op:
        batch_op.drop_column('question_ids')
        batch_op.alter_column('course_id', existing_type=sa.Integer(), nullable=False)
