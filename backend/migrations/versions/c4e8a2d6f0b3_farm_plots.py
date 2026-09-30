"""farm plots: optional field polygon per farm

Revision ID: c4e8a2d6f0b3
Revises: b7d2e4f6a8c1
Create Date: 2026-09-30 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4e8a2d6f0b3'
down_revision: Union[str, Sequence[str], None] = 'b7d2e4f6a8c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'farm_plots',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('farm_id', sa.String(), sa.ForeignKey('farms.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('geometry', sa.JSON(), nullable=False),
        sa.Column('area_ha', sa.Float(), nullable=False),
        sa.Column('crop', sa.String(), nullable=True),
        sa.Column('sowing_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('farm_plots')
