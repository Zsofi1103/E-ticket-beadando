# Testing Guide - Event-Ticket + Hotel Booking System

## Overview

This project uses **pytest** for unit testing, integration testing, and end-to-end testing. The testing framework ensures code quality, prevents regressions, and validates functionality.

## Test Structure

```
tests/
├── conftest.py           # Fixtures and configuration
├── test_models.py        # Unit tests for database models
├── test_routes.py        # Route/API endpoint tests
└── test_integration.py   # Integration and workflow tests
```

## Setup

### 1. Install Test Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage reporting
- `pytest-flask` - Flask-specific fixtures

### 2. Running Tests

#### Run All Tests
```bash
pytest
```

#### Run Specific Test File
```bash
pytest tests/test_models.py
```

#### Run Specific Test Class
```bash
pytest tests/test_models.py::TestUserModel
```

#### Run Specific Test Function
```bash
pytest tests/test_models.py::TestUserModel::test_user_creation
```

### 3. Test Coverage

Generate code coverage report:
```bash
pytest --cov=WebApp tests/
```

Generate coverage with HTML report:
```bash
pytest --cov=WebApp --cov-report=html tests/
```

This generates `htmlcov/index.html` with detailed coverage information.

### 4. Verbose Output

Run tests with detailed output:
```bash
pytest -v
```

Run with extra verbose output (including print statements):
```bash
pytest -vv
```

## Test Fixtures

Fixtures are reusable test components defined in `conftest.py`:

### Available Fixtures

1. **`app_context`** - Flask application context with SQLite database
2. **`client`** - Test client for making HTTP requests
3. **`runner`** - CLI runner for Flask commands
4. **`init_database`** - Initialized test database with sample data
5. **`authenticated_client`** - Client logged in as regular user
6. **`admin_client`** - Client logged in as admin user

### Using Fixtures in Tests

```python
def test_something(authenticated_client, init_database):
    """Test function using fixtures"""
    response = authenticated_client.get('/guest/bookings')
    assert response.status_code == 200
```

## Test Categories

### Unit Tests (`test_models.py`)

Test individual model components:

- **TestUserModel** - User creation, password hashing, role checks
- **TestRoomModel** - Room creation, availability checking
- **TestBookingModel** - Booking creation, calculations

Run unit tests:
```bash
pytest tests/test_models.py -v
```

### Route Tests (`test_routes.py`)

Test Flask routes and API endpoints:

- **TestEventRoutes** - Event listing, details, API
- **TestBookingRoutes** - Room search, booking views
- **TestAdminRoutes** - Admin functionality
- **TestAuthRoutes** - Authentication workflows
- **TestErrorHandling** - 404 and error pages

Run route tests:
```bash
pytest tests/test_routes.py -v
```

### Integration Tests (`test_integration.py`)

Test complete workflows:

- **TestBookingWorkflow** - Full booking process from search to confirmation
- **TestEventWithRooms** - Event and room integration
- **TestUserBookingHistory** - Booking history and profile
- **TestAdminRoomManagement** - Admin CRUD operations
- **TestDataConsistency** - Data integrity across operations

Run integration tests:
```bash
pytest tests/test_integration.py -v
```

## Sample Test Data

The `init_database` fixture automatically creates:

1. **Users:**
   - Regular user: `test@example.com` / `password123`
   - Admin user: `admin@example.com` / `admin123`

2. **Entities:**
   - 1 Event: "Test Event" on venue with price 50 HUF
   - 1 Venue: "Test Venue" with capacity 100
   - 1 Room: "101" with capacity 2, price 100 HUF/night
   - 1 Category: "Test Category"

## Common Test Patterns

### Test Authenticated Access

```python
def test_booking_page_requires_auth(client):
    response = client.get('/guest/bookings')
    assert response.status_code == 302  # Redirect to login
```

### Test Admin-Only Routes

```python
def test_admin_rooms_requires_admin(client):
    response = client.get('/admin/rooms')
    assert response.status_code == 403  # Forbidden
```

### Test Database Operations

```python
def test_create_booking(init_database, db):
    room = Room.query.first()
    user = User.query.first()
    
    booking = Booking(
        user_id=user.id,
        room_id=room.id,
        check_in=datetime.now(),
        check_out=datetime.now() + timedelta(days=2),
        guests_count=2
    )
    db.session.add(booking)
    db.session.commit()
    
    assert booking.id is not None
```

### Test API Response Format

```python
def test_api_events(client):
    response = client.get('/api/events')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'events' in data
    assert isinstance(data['events'], list)
```

## Debugging Tests

### Print Debug Information

```python
def test_something(client):
    response = client.get('/some-page')
    print(response.data)  # Print HTML/JSON response
    assert response.status_code == 200
```

Run with output:
```bash
pytest -s tests/test_routes.py::TestEventRoutes::test_index_page_loads
```

### Use pytest breakpoint

```python
def test_something():
    x = 5
    pytest.set_trace()  # Debugger will stop here
    assert x == 5
```

### Inspect Database State

```python
def test_with_inspection(init_database, db):
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"  - {user.email}: {user.role}")
```

## Continuous Integration (CI/CD)

To integrate tests into CI/CD pipeline:

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.14
      - run: pip install -r requirements.txt
      - run: pytest --cov=WebApp tests/
```

## Code Coverage Goals

- **Overall coverage:** > 80%
- **Critical paths:** 100% (auth, payments, bookings)
- **Models:** > 85%
- **Routes:** > 75%

## Best Practices

1. **Use descriptive test names** - `test_admin_can_create_room_with_valid_data`
2. **Test one thing per test** - Single assertion or clear workflow
3. **Use fixtures for setup** - Don't duplicate database initialization
4. **Test edge cases** - Empty data, invalid input, boundary conditions
5. **Keep tests independent** - No test should depend on another
6. **Use meaningful assertions** - Include error messages

## Troubleshooting

### Tests fail with "Database locked" error

This usually means SQLite database is being used. Ensure `TESTING=true` environment variable is set.

### Import errors for models

Ensure Flask app context is active:
```python
def test_something(app_context):
    from WebApp.models import User
    assert User is not None
```

### Fixture not found error

Check that `conftest.py` is in the `tests/` directory and fixtures are properly defined.

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-flask](https://pytest-flask.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/orm/session_basics.html#testing)

---

**Last Updated:** 2026-05-17  
**Coverage Target:** 80%+  
**Test Framework:** pytest 7.4.3+
