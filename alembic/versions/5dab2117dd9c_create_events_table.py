"""create events table

Revision ID: 5dab2117dd9c
Revises: 57fc85862bac
Create Date: 2025-06-14 18:31:08.600157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dab2117dd9c'
down_revision: Union[str, None] = '57fc85862bac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('person_name', sa.String(), nullable=True))
    op.create_index(op.f('ix_events_person_name'), 'events', ['person_name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_events_person_name'), table_name='events')
    op.drop_column('events', 'person_name')
    # ### end Alembic commands ###
