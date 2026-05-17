# Fejlesztési Irányelvek

## Kódolási Szabványok

### Python Kódolás

```python
# Jó
def calculate_booking_price(nights: int, price_per_night: float) -> float:
    """Calculate total booking price.
    
    Args:
        nights: Number of nights
        price_per_night: Nightly rate in HUF
        
    Returns:
        Total price
    """
    return nights * price_per_night

# Rossz
def calc_price(n, p):
    return n*p
```

#### Docstring Formátum
```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description
        
    Raises:
        ExceptionType: When/why raised
        
    Example:
        >>> function_name(1, 2)
        3
    """
```

### Model Definition

```python
# Jó
class Booking(db.Model):
    """Represents a hotel room booking"""
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    status = db.Column(Enum(BookingStatus), default=BookingStatus.pending)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"))
    
    # Relationships
    user = db.relationship('User', back_populates='bookings')
    room = db.relationship('Room', back_populates='bookings')
    
    def calculate_nights(self) -> int:
        """Calculate number of nights for booking"""
        return (self.check_out - self.check_in).days
```

### Error Handling

```python
# Jó
try:
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted', 'success')
except SQLAlchemyError as e:
    db.session.rollback()
    app.logger.error(f'Database error: {e}')
    flash('Error deleting booking', 'error')
except Exception as e:
    app.logger.exception(f'Unexpected error: {e}')
    flash('Unexpected error', 'error')

# Rossz
try:
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
except:
    pass
```

## Verziókezelés & Git Workflow

### Branch Elnevezés

```
feature/feature-name       # Új funkció
bugfix/bug-description     # Bugfix
hotfix/urgent-fix          # Sürgős javítás
refactor/improvement       # Refactor
docs/documentation         # Dokumentáció
test/test-coverage         # Tesztek
```

### Commit Üzenet

```
Jó:
- "Add room availability checking algorithm"
- "Fix booking conflict detection bug"
- "Update OpenAPI documentation"

Rossz:
- "fix bug"
- "update stuff"
- "working on it"
```

## Testing Best Practices

### Test Fedettség

```
Minimum requirements:
- Unit tests: 80% code coverage
- Critical paths: 100% coverage
- Models: 85% coverage
- Routes: 75% coverage
```

### Test Template

```python
def test_specific_scenario(fixture1, fixture2):
    """
    Test description: What is being tested and expected outcome
    
    Given: Initial conditions
    When: Action taken
    Then: Expected result
    """
    # Arrange
    data = prepare_test_data()
    
    # Act
    result = perform_action(data)
    
    # Assert
    assert result.is_valid()
    assert result.status == 'success'
```

## Dokumentáció Követelmények

### Docstring Kötelezettség

```python
# KÖTELEZŐ:
- Összes publikus függvény
- Összes osztály
- Összes modell
- Összes komplexebb metódus

# OPCIONÁLIS:
- Privát (_) függvények
- Egyszerű property getterek
```

### README Frissítés

Új funkció hozzáadása után frissítsd:
- README.md - Feature lista
- ARCHITECTURE.md - Komponens diagram
- TESTING.md - Új tesztek
- API dokumentáció

## Biztonsági Felülvizsgálat

### Security Checklist

- [ ] Input validáció (WTForms)
- [ ] SQL injection védelem (SQLAlchemy ORM)
- [ ] XSS védelem (Jinja2 escaping)
- [ ] CSRF protection (WTForms token)
- [ ] Authentication szükséges? (@login_required)
- [ ] Authorization ellenőrzés? (@admin_required)
- [ ] Audit logging? (AuditLog model)
- [ ] Error messages ne tárjanak fel infót
- [ ] Jelszó kezelés (hashing, salting)
- [ ] Rate limiting implementálva?

## Performance Optimization

### Database Queries

```python
# Jó - Lazy loading
bookings = Booking.query.filter_by(user_id=user_id).all()
for booking in bookings:
    room = booking.room  # Lazy-loaded if needed

# Jó - Eager loading
bookings = Booking.query.options(
    joinedload(Booking.room),
    joinedload(Booking.user)
).filter_by(status='pending').all()

# Rossz - N+1 query problem
bookings = Booking.query.all()
for booking in bookings:
    room_name = booking.room.name  # Extra query per booking!
```

### Pagination

```python
# Jó - paginated results
page = request.args.get('page', 1, type=int)
per_page = 20
items = Item.query.paginate(page=page, per_page=per_page)

# Rossz - fetch all
all_items = Item.query.all()
```

## Deployment Checklist

### Pre-Production

- [ ] Tesztek átmennek? (`pytest`)
- [ ] Code coverage > 80%? (`pytest --cov`)
- [ ] Linting clean? (`flake8`, `black`)
- [ ] Dokumentáció aktuális?
- [ ] Security review befejezve?
- [ ] Database migration tested?
- [ ] Environment variables beállítva?
- [ ] Backup strategy implementálva?

### Post-Production

- [ ] Alkalmazás fut-e? (health check)
- [ ] Error logging működik-e?
- [ ] Database backup OK?
- [ ] Monitoring aktív?
- [ ] Rollback plan kész?

## Code Review Kritériumok

### Reviewer Checklist

- [ ] Kód megfelel a szabványoknak
- [ ] Tesztek lefedik az új kódot
- [ ] Dokumentáció frissítve
- [ ] Nincs hardcoded értékek
- [ ] Biztonság ellenőrzve
- [ ] Performance-re figyeltek
- [ ] Error handling implementálva

## Közreműködési Folyamat

1. **Fork & Clone**
   ```bash
   git clone https://github.com/user/repo.git
   ```

2. **Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Fejlesztés**
   ```bash
   # Tesztek írása
   pytest tests/
   
   # Kód formázása
   black WebApp/
   
   # Linting
   flake8 WebApp/
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

5. **Pull Request**
   - Describa a változásokat
   - Reference GitHub issues
   - Expect review

## Debugging Tips

### Flask Debug Mode

```bash
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py
```

### Database Inspection

```python
# SQLite
sqlite3 hotelbooking.db
.tables
.schema booking

# MySQL
mysql -u user -p database_name
SHOW TABLES;
DESCRIBE booking;
```

### Logging

```python
# Development
app.logger.debug(f"Value: {value}")

# Production (errors only)
app.logger.error(f"Error: {error}")
app.logger.exception(f"Exception: {e}")
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pytest Guide](https://docs.pytest.org/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Workflow](https://git-scm.com/book/)

---

**Utolsó frissítés:** 2026-05-17
