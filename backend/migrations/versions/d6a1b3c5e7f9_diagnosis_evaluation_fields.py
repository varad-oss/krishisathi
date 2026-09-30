"""diagnosis evaluation fields: image quality, guidance level, differential, model version

Revision ID: d6a1b3c5e7f9
Revises: c4e8a2d6f0b3
Create Date: 2026-09-30 13:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd6a1b3c5e7f9'
down_revision: Union[str, Sequence[str], None] = 'c4e8a2d6f0b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.add_column(sa.Column('image_quality', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('guidance_level', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('differential', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('model_version', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.drop_column('model_version')
        batch_op.drop_column('differential')
        batch_op.drop_column('guidance_level')
        batch_op.drop_column('image_quality')
