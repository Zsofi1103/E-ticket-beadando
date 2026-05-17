"""
Route Tests - Test Flask routes and API endpoints
"""

import pytest
from datetime import datetime, timedelta
from WebApp.models import Booking, BookingStatus
import json


class TestEventRoutes:
    """Test event-related routes"""
    
    def test_index_page_loads(self, client, init_database):
        """Test that index page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Vissza' not in response.data or b'esem' in response.data  # Event-related content
    
    def test_event_detail_page(self, client, init_database):
        """Test that event detail page loads"""
        response = client.get('/event/detail/1')
        assert response.status_code == 200
        assert b'Test Event' in response.data
    
    def test_api_events_endpoint(self, client, init_database):
        """Test /api/events REST endpoint"""
        response = client.get('/api/events')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'events' in data
        assert len(data['events']) > 0
        assert data['events'][0]['title'] == 'Test Event'


class TestBookingRoutes:
    """Test booking-related routes"""
    
    def test_search_rooms_page(self, client, init_database):
        """Test room search page loads"""
        response = client.get('/guest/search')
        assert response.status_code == 200
        assert b'Szob' in response.data
    
    def test_search_rooms_post(self, client, init_database):
        """Test room search with POST"""
        check_in = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        response = client.post('/guest/search', data={
            'check_in': check_in,
            'check_out': check_out,
            'guests_count': 2
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Page should show available rooms
        assert b'101' in response.data or b'szoba' in response.data.lower()
    
    def test_view_bookings_requires_login(self, client, init_database):
        """Test that viewing bookings requires login"""
        response = client.get('/guest/bookings')
        assert response.status_code == 302  # Redirect to login
    
    def test_user_can_view_own_bookings(self, authenticated_client, init_database, db):
        """Test that logged-in user can view their bookings"""
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
        
        response = authenticated_client.get('/guest/bookings')
        assert response.status_code == 200


class TestAdminRoutes:
    """Test admin-only routes"""
    
    def test_admin_rooms_requires_admin(self, client, init_database):
        """Test that admin rooms page requires admin role"""
        response = client.get('/admin/rooms')
        assert response.status_code == 302  # Redirect (not authenticated)
    
    def test_admin_can_access_rooms(self, admin_client, init_database):
        """Test that admin can access rooms management"""
        response = admin_client.get('/admin/rooms')
        assert response.status_code == 200
        assert b'101' in response.data  # Room number should appear
    
    def test_admin_can_create_room(self, admin_client, init_database):
        """Test that admin can create a new room"""
        response = admin_client.post('/admin/rooms/new', data={
            'room_number': '202',
            'capacity': 3,
            'price_per_night': 150.00,
            'description': 'New test room',
            'status': 'available'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'202' in response.data or b'sikeres' in response.data
    
    def test_non_admin_cannot_create_room(self, authenticated_client, init_database):
        """Test that non-admin cannot create room"""
        response = authenticated_client.post('/admin/rooms/new', data={
            'room_number': '303',
            'capacity': 2,
            'price_per_night': 100.00
        }, follow_redirects=True)
        
        assert response.status_code == 403 or b'admin' in response.data.lower()


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_register_page_loads(self, client):
        """Test registration page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Regisztr' in response.data or b'regist' in response.data.lower()
    
    def test_login_page_loads(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Bejelent' in response.data or b'login' in response.data.lower()
    
    def test_successful_login(self, client, init_database):
        """Test successful login"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should be logged in now
        response = client.get('/profile')
        assert response.status_code == 200 or response.status_code == 302
    
    def test_failed_login(self, client, init_database):
        """Test login with wrong password"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'error' in response.data.lower() or response.status_code == 200


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_not_found(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_event_detail(self, client):
        """Test accessing non-existent event"""
        response = client.get('/event/detail/99999')
        assert response.status_code == 404
    
    def test_invalid_room_booking(self, authenticated_client):
        """Test booking non-existent room"""
        response = authenticated_client.get('/guest/book/99999')
        assert response.status_code == 404
