"""add users and ownership

Revision ID: 301b0fd2d7f8
Revises: 20251108_013735
Create Date: 2025-11-07 22:57:07.932815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '301b0fd2d7f8'
down_revision = '20251108_013735'
branch_labels = None
depends_on = None


def upgrade():
    user_table = op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='member'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    op.bulk_insert(
        user_table,
        [
            {
                "id": 1,
                "email": "household@example.com",
                "password_hash": "scrypt:32768:8:1$F2SahGfBCxW2LoOv$73351f0bfc99a5d12a4d399b201993bfbba37442bd867b4cffc95d6616278974119c819ea1b9540363d8f04be72b5eaec60b25b381dc23dc0862ff3d885ebc5c",
                "role": "owner",
            }
        ],
    )

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

    op.execute(sa.text('UPDATE asset SET user_id = 1'))

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_index('ix_asset_user_id', ['user_id'])
        batch_op.create_foreign_key('fk_asset_user_id_user', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

    op.execute(sa.text('UPDATE task SET user_id = 1'))

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_index('ix_task_user_id', ['user_id'])
        batch_op.create_foreign_key('fk_task_user_id_user', 'user', ['user_id'], ['id'])

    op.create_index(op.f('ix_task_asset_id'), 'task', ['asset_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_task_asset_id'), table_name='task')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('fk_task_user_id_user', type_='foreignkey')
        batch_op.drop_index('ix_task_user_id')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.drop_constraint('fk_asset_user_id_user', type_='foreignkey')
        batch_op.drop_index('ix_asset_user_id')
        batch_op.drop_column('user_id')

    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
