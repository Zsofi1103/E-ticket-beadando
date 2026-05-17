"""
Model Tests - Test database models and their relationships
"""

import pytest
from datetime import datetime, timedelta
from WebApp.models import User, Room, Booking, BookingStatus
from werkzeug.security import check_password_hash, generate_password_hash


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, init_database):
        """Test creating a new user"""
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.name == 'Test User'
        assert user.email == 'test@example.com'
    
    def test_password_hashing(self, init_database):
        """Test that password is properly hashed"""
        user = User.query.filter_by(email='test@example.com').first()
        assert user.password != 'password123'
        assert check_password_hash(user.password, 'password123')
    
    def test_admin_role(self, init_database):
        """Test admin role check"""
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin.is_admin() is True
        
        regular = User.query.filter_by(email='test@example.com').first()
        assert regular.is_admin() is False
    
    def test_user_repr(self, init_database):
        """Test user string representation"""
        user = User.query.filter_by(email='test@example.com').first()
        assert repr(user) is not None
        assert 'Test User' in repr(user)


class TestRoomModel:
    """Test Room model functionality"""
    
    def test_room_creation(self, init_database):
        """Test creating a new room"""
        room = Room.query.filter_by(room_number='101').first()
        assert room is not None
        assert room.capacity == 2
        assert room.price_per_night == 100.00
    
    def test_room_availability_check(self, init_database, db):
        """Test room availability checking"""
        room = Room.query.filter_by(room_number='101').first()
        user = User.query.filter_by(email='test@example.com').first()
        
        check_in = datetime.now() + timedelta(days=1)
        check_out = datetime.now() + timedelta(days=3)
        
        # Room should be available initially
        assert room.is_available(check_in, check_out) is True
        
        # Create a booking
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests_count=2,
            status=BookingStatus.confirmed,
            total_price=200.00
        )
        db.session.add(booking)
        db.session.commit()
        
        # Room should now be unavailable for overlapping dates
        overlap_check_in = datetime.now() + timedelta(days=2)
        overlap_check_out = datetime.now() + timedelta(days=4)
        assert room.is_available(overlap_check_in, overlap_check_out) is False
        
        # Room should be available for non-overlapping dates
        after_check_in = datetime.now() + timedelta(days=5)
        after_check_out = datetime.now() + timedelta(days=7)
        assert room.is_available(after_check_in, after_check_out) is True
    
    def test_room_repr(self, init_database):
        """Test room string representation"""
        room = Room.query.filter_by(room_number='101').first()
        assert '101' in repr(room)
        assert '2 ágyas' in repr(room)


class TestBookingModel:
    """Test Booking model functionality"""
    
    def test_booking_creation(self, init_database, db):
        """Test creating a new booking"""
        room = Room.query.filter_by(room_number='101').first()
        user = User.query.filter_by(email='test@example.com').first()
        
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=datetime.now() + timedelta(days=1),
            check_out=datetime.now() + timedelta(days=3),
            guests_count=2,
            status=BookingStatus.pending,
            total_price=200.00
        )
        db.session.add(booking)
        db.session.commit()
        
        retrieved = Booking.query.first()
        assert retrieved is not None
        assert retrieved.guests_count == 2
        assert retrieved.status == BookingStatus.pending
    
    def test_booking_nights_calculation(self, init_database, db):
        """Test nights calculation"""
        room = Room.query.filter_by(room_number='101').first()
        user = User.query.filter_by(email='test@example.com').first()
        
        check_in = datetime.now()
        check_out = check_in + timedelta(days=3)
        
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests_count=2,
            total_price=300.00
        )
        db.session.add(booking)
        db.session.commit()
        
        nights = booking.calculate_nights()
        assert nights == 3
    
    def test_booking_price_calculation(self, init_database, db):
        """Test total price calculation"""
        room = Room.query.filter_by(room_number='101').first()
        user = User.query.filter_by(email='test@example.com').first()
        
        check_in = datetime.now()
        check_out = check_in + timedelta(days=2)
        
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests_count=2,
            total_price=200.00
        )
        db.session.add(booking)
        db.session.commit()
        
        total_price = booking.calculate_total_price()
        expected_price = float(room.price_per_night) * 2
        assert total_price == expected_price
