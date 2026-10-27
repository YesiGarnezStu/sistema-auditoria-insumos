"""Crear food_images y sensor_readings

Revision ID: 21a62c3f4009
Revises: 21a62c3f4008
Create Date: 2026-10-14 17:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '21a62c3f4009'
down_revision: Union[str, Sequence[str], None] = '21a62c3f4008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Crear tabla sensor_readings
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('refrigerator_id', sa.String(length=36), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('door_open', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['refrigerator_id'], ['refrigerators.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_readings_id'), 'sensor_readings', ['id'], unique=False)
    op.create_index(op.f('ix_sensor_readings_refrigerator_id'), 'sensor_readings', ['refrigerator_id'], unique=False)
    op.create_index(op.f('ix_sensor_readings_created_at'), 'sensor_readings', ['created_at'], unique=False)

    # 2. Crear tabla food_images
    op.create_table(
        'food_images',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('food_id', sa.String(length=36), nullable=True),
        sa.Column('ticket_id', sa.String(length=36), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=False),
        sa.Column('image_type', sa.String(length=50), nullable=True),
        sa.Column('ocr_extracted_text', sa.Text(), nullable=True),
        sa.Column('ai_analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id']),
        sa.ForeignKeyConstraint(['ticket_id'], ['purchase_tickets.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_images_id'), 'food_images', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_food_images_id'), table_name='food_images')
    op.drop_table('food_images')
    op.drop_index(op.f('ix_sensor_readings_created_at'), table_name='sensor_readings')
    op.drop_index(op.f('ix_sensor_readings_refrigerator_id'), table_name='sensor_readings')
    op.drop_index(op.f('ix_sensor_readings_id'), table_name='sensor_readings')
    op.drop_table('sensor_readings')
