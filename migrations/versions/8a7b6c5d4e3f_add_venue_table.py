"""add venue table and venue_id FK on event

Revision ID: 8a7b6c5d4e3f
Revises: fa5666ef4661
Create Date: 2025-12-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8a7b6c5d4e3f'
down_revision = 'fa5666ef4661'
branch_labels = None
depends_on = None


def upgrade():
    # Create venue table
    op.create_table(
        'venue',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
    )

    # Add venue_id column to event table
    op.add_column('event', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_event_venue', 'event', 'venue', ['venue_id'], ['id'])


def downgrade():
    # Drop foreign key and column, then drop venue table
    try:
        op.drop_constraint('fk_event_venue', 'event', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_column('event', 'venue_id')
    except Exception:
        pass
    op.drop_table('venue')
