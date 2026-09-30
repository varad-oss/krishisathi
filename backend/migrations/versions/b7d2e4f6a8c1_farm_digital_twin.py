"""farm digital twin: farms, intelligence snapshots, advisory actions with outcomes; diagnoses.farm_id

Revision ID: b7d2e4f6a8c1
Revises: a1c3e5f7b9d2
Create Date: 2026-09-30 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7d2e4f6a8c1'
down_revision: Union[str, Sequence[str], None] = 'a1c3e5f7b9d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'farms',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('crop', sa.String(), nullable=True),
        sa.Column('sowing_date', sa.Date(), nullable=True),
        sa.Column('area_ha', sa.Float(), nullable=True),
    )
    op.create_index('ix_farms_crop', 'farms', ['crop'])
    op.create_index('ix_farms_location', 'farms', ['lat', 'lng'])

    op.create_table(
        'farm_snapshots',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('farm_id', sa.String(), sa.ForeignKey('farms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('crop', sa.String(), nullable=True),
        sa.Column('crop_stage', sa.String(), nullable=True),
        sa.Column('top_action', sa.String(), nullable=True),
        sa.Column('top_severity', sa.String(), nullable=True),
        sa.Column('risks', sa.JSON(), nullable=False),
        sa.Column('data_quality', sa.JSON(), nullable=False),
        sa.Column('observations', sa.JSON(), nullable=True),
    )
    op.create_index('ix_farm_snapshots_farm_time', 'farm_snapshots', ['farm_id', 'created_at'])

    op.create_table(
        'advisory_actions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('farm_id', sa.String(), sa.ForeignKey('farms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_ref', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('confidence', sa.String(), nullable=True),
        sa.Column('crop', sa.String(), nullable=True),
        sa.Column('followed', sa.String(), nullable=True),
        sa.Column('followed_at', sa.DateTime(), nullable=True),
        sa.Column('outcome', sa.String(), nullable=True),
        sa.Column('outcome_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_advisory_actions_created_at', 'advisory_actions', ['created_at'])
    op.create_index('ix_advisory_actions_action', 'advisory_actions', ['action'])
    op.create_index('ix_advisory_actions_crop', 'advisory_actions', ['crop'])
    op.create_index('ix_advisory_actions_farm_time', 'advisory_actions', ['farm_id', 'created_at'])

    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.add_column(sa.Column('farm_id', sa.String(), nullable=True))
        batch_op.create_index('ix_diagnoses_farm_id', ['farm_id'])
        batch_op.create_foreign_key('fk_diagnoses_farm_id', 'farms', ['farm_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.drop_constraint('fk_diagnoses_farm_id', type_='foreignkey')
        batch_op.drop_index('ix_diagnoses_farm_id')
        batch_op.drop_column('farm_id')
    op.drop_table('advisory_actions')
    op.drop_table('farm_snapshots')
    op.drop_index('ix_farms_location', table_name='farms')
    op.drop_index('ix_farms_crop', table_name='farms')
    op.drop_table('farms')
