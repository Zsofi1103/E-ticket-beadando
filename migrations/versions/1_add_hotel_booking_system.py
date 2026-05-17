"""Add hotel booking system tables

Revision ID: 1_add_hotel_booking_system
Revises: fa5666ef4661_merge_heads
Create Date: 2026-05-17 12:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1_add_hotel_booking_system'
down_revision = 'fa5666ef4661_merge_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Create room table
    op.create_table(
        'room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(50), nullable=False, unique=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('price_per_night', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('equipment', sa.String(500), nullable=True),
        sa.Column('status', sa.Enum('available', 'occupied', 'maintenance', 'unavailable'), 
                  nullable=False, server_default='available'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), 
                  onupdate=sa.func.utc_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_room_room_number', 'room', ['room_number'])
    
    # Add bookings table
    op.create_table(
        'booking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.DateTime(), nullable=False),
        sa.Column('check_out', sa.DateTime(), nullable=False),
        sa.Column('guests_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled'), 
                  nullable=False, server_default='pending'),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('check_out_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), 
                  onupdate=sa.func.utc_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_booking_user_id', 'booking', ['user_id'])
    op.create_index('ix_booking_room_id', 'booking', ['room_id'])
    op.create_index('ix_booking_status', 'booking', ['status'])
    
    # Add extra_service table
    op.create_table(
        'extra_service',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add booking_service table (N:N relationship)
    op.create_table(
        'booking_service',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['extra_service.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_booking_service_booking_id', 'booking_service', ['booking_id'])
    op.create_index('ix_booking_service_service_id', 'booking_service', ['service_id'])
    
    # Add invoice table
    op.create_table(
        'invoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('paid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invoice_booking_id', 'invoice', ['booking_id'])
    
    # Add permission table
    op.create_table(
        'permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add role_permission table
    op.create_table(
        'role_permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_name', sa.String(50), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_role_permission_role_name', 'role_permission', ['role_name'])
    
    # Add audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.utc_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_booking_id', 'audit_log', ['booking_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    
    # Modify user table to support new roles and add new fields
    op.add_column('user', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('user', sa.Column('address', sa.String(500), nullable=True))


def downgrade():
    # Drop all new tables
    op.drop_table('audit_log')
    op.drop_table('role_permission')
    op.drop_table('permission')
    op.drop_table('invoice')
    op.drop_table('booking_service')
    op.drop_table('extra_service')
    op.drop_table('booking')
    op.drop_table('room')
    
    # Revert user table changes
    op.drop_column('user', 'address')
    op.drop_column('user', 'phone')
