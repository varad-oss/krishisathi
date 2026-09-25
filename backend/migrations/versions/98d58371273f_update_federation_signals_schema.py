"""update federation signals schema

Revision ID: 98d58371273f
Revises: cb173cba2f09
Create Date: 2026-09-25 13:34:20.337671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98d58371273f'
down_revision: Union[str, Sequence[str], None] = 'cb173cba2f09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('federation_signals') as batch_op:
        batch_op.add_column(sa.Column('signal_metadata', sa.JSON(), nullable=True))
        batch_op.alter_column('to_state',
                   existing_type=sa.VARCHAR(),
                   nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('federation_signals') as batch_op:
        batch_op.alter_column('to_state',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
        batch_op.drop_column('signal_metadata')
