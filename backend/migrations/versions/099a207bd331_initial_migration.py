"""Initial migration

Revision ID: 099a207bd331
Revises: 
Create Date: 2025-03-06 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '099a207bd331'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Uwaga: to rozwiązanie usunie istniejące tabele i wszystkie dane w nich.
    op.execute("DROP TABLE IF EXISTS white_cards CASCADE")
    op.execute("DROP TABLE IF EXISTS black_cards CASCADE")

    op.create_table(
        'black_cards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'white_cards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_black_cards_id', 'black_cards', ['id'], unique=False)
    op.create_index('ix_white_cards_id', 'white_cards', ['id'], unique=False)

def downgrade():
    op.drop_index('ix_black_cards_id', table_name='black_cards')
    op.drop_index('ix_white_cards_id', table_name='white_cards')
    op.drop_table('white_cards')
    op.drop_table('black_cards')
