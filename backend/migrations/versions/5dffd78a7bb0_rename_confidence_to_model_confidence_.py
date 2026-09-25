"""rename confidence to model_confidence_score and update severity fields

Revision ID: 5dffd78a7bb0
Revises: 12684fe24aab
Create Date: 2026-09-25 19:24:41.262011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dffd78a7bb0'
down_revision: Union[str, Sequence[str], None] = '12684fe24aab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.alter_column('confidence', new_column_name='model_confidence_score')
        batch_op.alter_column('severity', new_column_name='model_inferred_severity')
        batch_op.alter_column('spread_risk', new_column_name='model_inferred_spread_risk')
        
    with op.batch_alter_table('outbreaks') as batch_op:
        batch_op.alter_column('severity', new_column_name='aggregated_severity')

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('outbreaks') as batch_op:
        batch_op.alter_column('aggregated_severity', new_column_name='severity')
        
    with op.batch_alter_table('diagnoses') as batch_op:
        batch_op.alter_column('model_inferred_spread_risk', new_column_name='spread_risk')
        batch_op.alter_column('model_inferred_severity', new_column_name='severity')
        batch_op.alter_column('model_confidence_score', new_column_name='confidence')
