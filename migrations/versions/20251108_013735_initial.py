
"""initial

Revision ID: 20251108_013735
Revises: 
Create Date: 2025-11-08T01:37:35.249020

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251108_013735'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('asset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('make', sa.String(length=120), nullable=True),
        sa.Column('model', sa.String(length=120), nullable=True),
        sa.Column('serial', sa.String(length=120), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('warranty_expiration', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_name'), 'asset', ['name'], unique=False)
    op.create_index(op.f('ix_asset_serial'), 'asset', ['serial'], unique=False)
    op.create_index(op.f('ix_asset_type'), 'asset', ['type'], unique=False)

    op.create_table('task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('recurrence_rule', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('pending','done','skipped','deleted', name='task_status'), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Numeric(10,2), nullable=True),
        sa.Column('vendor', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['asset.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_due_date'), 'task', ['due_date'], unique=False)
    op.create_index(op.f('ix_task_status'), 'task', ['status'], unique=False)
    op.create_index(op.f('ix_task_title'), 'task', ['title'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_task_title'), table_name='task')
    op.drop_index(op.f('ix_task_status'), table_name='task')
    op.drop_index(op.f('ix_task_due_date'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_asset_type'), table_name='asset')
    op.drop_index(op.f('ix_asset_serial'), table_name='asset')
    op.drop_index(op.f('ix_asset_name'), table_name='asset')
    op.drop_table('asset')
