"""store diagnosis status and qualitative certainty; relax legacy numeric confidence

Revision ID: a1c3e5f7b9d2
Revises: 5dffd78a7bb0
Create Date: 2026-09-26 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c3e5f7b9d2'
down_revision: Union[str, Sequence[str], None] = '5dffd78a7bb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.add_column(sa.Column('diagnosis_status', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('certainty', sa.String(), nullable=True))
        batch_op.alter_column('model_confidence_score', existing_type=sa.Float(), nullable=True)
        batch_op.alter_column('model_inferred_severity', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('model_inferred_spread_risk', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('lat', existing_type=sa.Float(), nullable=True)
        batch_op.alter_column('lng', existing_type=sa.Float(), nullable=True)
        batch_op.create_index('ix_diagnoses_diagnosis_status', ['diagnosis_status'])


def downgrade() -> None:
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.drop_index('ix_diagnoses_diagnosis_status')
        batch_op.drop_column('certainty')
        batch_op.drop_column('diagnosis_status')
