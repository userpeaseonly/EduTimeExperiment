"""create events table

Revision ID: d2fa5c1fcc1e
Revises: 5dab2117dd9c
Create Date: 2025-06-14 20:47:16.329480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd2fa5c1fcc1e'
down_revision: Union[str, None] = '5dab2117dd9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'event_metadata')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
