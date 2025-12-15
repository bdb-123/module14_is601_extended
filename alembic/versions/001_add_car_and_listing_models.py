"""Add Car and Listing models for CarCompare feature

Revision ID: 001
Revises: 
Create Date: 2025-12-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create Car and Listing tables for the CarCompare feature.
    
    This migration adds:
    - cars table: Stores user vehicles with VIN, make, model, year, etc.
    - listings table: Stores marketplace listings for cars
    
    Both tables have foreign keys to the users table with cascade deletes.
    """
    # Create cars table
    op.create_table('cars',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vin', sa.String(length=17), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('trim', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vin')
    )
    op.create_index(op.f('ix_cars_id'), 'cars', ['id'], unique=False)
    op.create_index(op.f('ix_cars_user_id'), 'cars', ['user_id'], unique=False)
    
    # Create listings table
    op.create_table('listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('car_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_listings_car_id'), 'listings', ['car_id'], unique=False)
    op.create_index(op.f('ix_listings_id'), 'listings', ['id'], unique=False)
    op.create_index(op.f('ix_listings_user_id'), 'listings', ['user_id'], unique=False)


def downgrade() -> None:
    """
    Drop Car and Listing tables.
    
    This will remove all cars and listings data. Use with caution!
    """
    op.drop_index(op.f('ix_listings_user_id'), table_name='listings')
    op.drop_index(op.f('ix_listings_id'), table_name='listings')
    op.drop_index(op.f('ix_listings_car_id'), table_name='listings')
    op.drop_table('listings')
    
    op.drop_index(op.f('ix_cars_user_id'), table_name='cars')
    op.drop_index(op.f('ix_cars_id'), table_name='cars')
    op.drop_table('cars')
