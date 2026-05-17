"""
Integration Tests - Test complete workflows and interactions between components
"""

import pytest
from datetime import datetime, timedelta
from WebApp.models import Booking, BookingStatus, User, Room
import json


class TestBookingWorkflow:
    """Test complete booking workflow"""
    
    def test_full_booking_workflow(self, authenticated_client, init_database, db):
        """Test complete booking process from search to confirmation"""
        
        # Step 1: Search for rooms
        check_in = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        search_response = authenticated_client.post('/guest/search', data={
            'check_in': check_in,
            'check_out': check_out,
            'guests_count': 2
        }, follow_redirects=True)
        
        assert search_response.status_code == 200
        
        # Step 2: Book a room
        room = db.session.query(Room).first()
        booking_response = authenticated_client.post(f'/guest/book/{room.id}', data={
            'check_in': check_in,
            'check_out': check_out,
            'guests_count': 2
        }, follow_redirects=True)
        
        assert booking_response.status_code == 200
        
        # Verify booking was created
        user = db.session.query(User).filter_by(email='test@example.com').first()
        booking = db.session.query(Booking).filter_by(user_id=user.id).first()
        assert booking is not None
        assert booking.room_id == room.id
    
    def test_booking_conflict_detection(self, authenticated_client, init_database, db):
        """Test that overlapping bookings are prevented"""
        
        room = db.session.query(Room).first()
        user = db.session.query(User).filter_by(email='test@example.com').first()
        
        # Create first booking
        check_in = datetime.now() + timedelta(days=1)
        check_out = datetime.now() + timedelta(days=3)
        
        booking1 = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests_count=2,
            status=BookingStatus.confirmed,
            total_price=200.00
        )
        db.session.add(booking1)
        db.session.commit()
        
        # Try to book overlapping dates
        overlap_check_in = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        overlap_check_out = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
        
        response = authenticated_client.post(f'/guest/book/{room.id}', data={
            'check_in': overlap_check_in,
            'check_out': overlap_check_out,
            'guests_count': 2
        }, follow_redirects=True)
        
        # Should fail or show error
        assert b'sabad' in response.data.lower() or b'conflict' in response.data.lower() or response.status_code in [400, 409]


class TestEventWithRooms:
    """Test event and room integration"""
    
    def test_event_shows_available_rooms(self, client, init_database):
        """Test that event detail page shows available rooms from venue"""
        
        response = client.get('/event/detail/1')
        assert response.status_code == 200
        
        # Should show room information
        assert b'101' in response.data or b'szob' in response.data.lower()
    
    def test_venue_with_multiple_rooms(self, init_database, db):
        """Test venue with multiple rooms"""
        from WebApp.models import Venue
        
        venue = db.session.query(Venue).first()
        room1 = db.session.query(Room).filter_by(venue_id=venue.id).first()
        
        # Verify room is associated with venue
        assert room1 is not None
        assert room1.venue_id == venue.id
        assert room1 in venue.rooms


class TestUserBookingHistory:
    """Test user booking history and profile"""
    
    def test_user_can_view_booking_history(self, authenticated_client, init_database, db):
        """Test that user can view their booking history"""
        
        room = db.session.query(Room).first()
        user = db.session.query(User).filter_by(email='test@example.com').first()
        
        # Create test booking
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=datetime.now() + timedelta(days=1),
            check_out=datetime.now() + timedelta(days=3),
            guests_count=2,
            status=BookingStatus.confirmed,
            total_price=200.00
        )
        db.session.add(booking)
        db.session.commit()
        
        response = authenticated_client.get('/guest/bookings')
        assert response.status_code == 200
        assert str(booking.id) in response.data.decode() or b'101' in response.data
    
    def test_user_can_view_single_booking(self, authenticated_client, init_database, db):
        """Test that user can view individual booking details"""
        
        room = db.session.query(Room).first()
        user = db.session.query(User).filter_by(email='test@example.com').first()
        
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=datetime.now() + timedelta(days=1),
            check_out=datetime.now() + timedelta(days=3),
            guests_count=2,
            status=BookingStatus.confirmed,
            total_price=200.00
        )
        db.session.add(booking)
        db.session.commit()
        
        response = authenticated_client.get(f'/guest/booking/{booking.id}')
        assert response.status_code == 200 or response.status_code == 302


class TestAdminRoomManagement:
    """Test admin room management workflows"""
    
    def test_admin_full_room_crud(self, admin_client, init_database, db):
        """Test complete CRUD operations on rooms by admin"""
        
        # Create
        create_response = admin_client.post('/admin/rooms/new', data={
            'room_number': '505',
            'capacity': 4,
            'price_per_night': 200.00,
            'description': 'Suite room',
            'status': 'available'
        }, follow_redirects=True)
        
        assert create_response.status_code == 200
        
        # Read
        list_response = admin_client.get('/admin/rooms')
        assert list_response.status_code == 200
        assert b'505' in list_response.data
        
        # Update
        room = db.session.query(Room).filter_by(room_number='505').first()
        if room:
            update_response = admin_client.post(f'/admin/rooms/{room.id}/edit', data={
                'room_number': '505',
                'capacity': 5,
                'price_per_night': 250.00,
                'status': 'available'
            }, follow_redirects=True)
            
            assert update_response.status_code == 200
            
            # Verify update
            updated_room = db.session.query(Room).filter_by(room_number='505').first()
            assert updated_room.capacity == 5
            assert updated_room.price_per_night == 250.00


class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_booking_total_price_updated(self, init_database, db):
        """Test that booking total price is correctly calculated"""
        
        room = db.session.query(Room).first()
        user = db.session.query(User).first()
        
        check_in = datetime.now()
        check_out = check_in + timedelta(days=5)
        
        booking = Booking(
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests_count=2,
            total_price=0
        )
        db.session.add(booking)
        db.session.commit()
        
        # Calculate total price
        total = booking.calculate_total_price()
        expected = float(room.price_per_night) * 5
        assert total == expected
    
    def test_room_venue_relationship(self, init_database, db):
        """Test room-venue relationship integrity"""
        
        from WebApp.models import Venue
        
        venue = db.session.query(Venue).first()
        room = db.session.query(Room).filter_by(venue_id=venue.id).first()
        
        assert room is not None
        assert room.venue == venue
        assert room in venue.rooms
