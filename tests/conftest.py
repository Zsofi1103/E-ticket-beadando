"""
Test Configuration and Fixtures
Pytest configuration file for the Event-Ticket + Hotel Booking application
"""

import pytest
import os
from WebApp import app, db
from WebApp.models import User, Event, Room, Booking, Category, Venue
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app_context():
    """Create application context for testing"""
    os.environ['TESTING'] = 'true'
    os.environ['FLASK_ENV'] = 'testing'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_context):
    """Create test client"""
    return app_context.test_client()


@pytest.fixture
def runner(app_context):
    """Create CLI runner"""
    return app_context.test_cli_runner()


@pytest.fixture
def init_database():
    """Initialize test database with sample data"""
    db.create_all()
    
    # Create test user
    user = User(
        name='Test User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        phone='1234567890',
        address='Test Address 1.'
    )
    db.session.add(user)
    
    # Create admin user
    admin = User(
        name='Admin User',
        email='admin@example.com',
        password=generate_password_hash('admin123'),
        phone='0987654321'
    )
    admin.role = 'admin'
    db.session.add(admin)
    
    # Create venue
    venue = Venue(
        name='Test Venue',
        address='123 Test Street',
        capacity=100
    )
    db.session.add(venue)
    db.session.flush()
    
    # Create event
    event = Event(
        title='Test Event',
        description='A test event',
        price=50.00,
        start_at=datetime.now() + timedelta(days=7),
        venue_id=venue.id
    )
    db.session.add(event)
    
    # Create category
    category = Category(name='Test Category')
    db.session.add(category)
    db.session.flush()
    
    event.categories.append(category)
    
    # Create room
    room = Room(
        room_number='101',
        capacity=2,
        price_per_night=100.00,
        description='A test room',
        status='available',
        venue_id=venue.id
    )
    db.session.add(room)
    
    db.session.commit()
    
    yield db
    
    db.session.remove()
    db.drop_all()


@pytest.fixture
def authenticated_client(client, init_database):
    """Create authenticated test client"""
    with client:
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def admin_client(client, init_database):
    """Create admin authenticated test client"""
    with client:
        client.post('/login', data={
            'email': 'admin@example.com',
            'password': 'admin123'
        }, follow_redirects=True)
        yield client
