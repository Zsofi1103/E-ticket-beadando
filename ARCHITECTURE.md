# Architektúra Dokumentáció - Event-Ticket + Hotel Booking System

## 1. Rendszer Áttekintés

Ez egy **3 rétegű web alkalmazás** Flask keretrendszerrel, amely két integrált funkciót valósít meg:

1. **Event Management System** - Esemény-foglalás
2. **Hotel Booking System** - Szobafoglalás a helyszínen

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/CSS/JS)                      │
├─────────────────────────────────────────────────────────────────┤
│  Templates: /WebApp/templates/ - Jinja2 templates, Bootstrap 5   │
├─────────────────────────────────────────────────────────────────┤
│                 Flask Application Layer                          │
├──────────────────────────────────────────────────────────────────┤
│  Routes (/WebApp/routes.py)      │  Blueprints (/WebApp/...)    │
│  - Event management              │  - guest_bp: szobakeresés    │
│  - User authentication           │  - admin_bp: adminisztráció  │
│  - API endpoints (/api/*)        │                              │
├──────────────────────────────────────────────────────────────────┤
│              Business Logic Layer                                 │
├──────────────────────────────────────────────────────────────────┤
│  Managers (/WebApp/managers/)    │  Forms (/WebApp/forms/)      │
│  - EventManager                  │  - WTForms validation        │
│  - Business rules               │  - CSRF protection           │
├──────────────────────────────────────────────────────────────────┤
│                  Data Access Layer (ORM)                          │
├──────────────────────────────────────────────────────────────────┤
│  SQLAlchemy Models (/WebApp/models/):                            │
│  - User, Event, Room, Booking, Venue, Category, etc.            │
│  - Relationships, constraints, enums                            │
├──────────────────────────────────────────────────────────────────┤
│                    Database Layer                                 │
├──────────────────────────────────────────────────────────────────┤
│  MySQL 8.0+ (Production)  │  SQLite (Development/Testing)       │
│  Alembic migrations        │  Automatic schema creation         │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Komponens Diagramm

### A. Felhasználói Folyamatok

```
┌─────────────────┐
│    Felhasználó  │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │           │          │
    v           v          v
 Login      Esemény    Szobakeresés
   │        Listázás        │
   │            │           │
   └──────┬──────┴────┬──────┘
          │           │
          v           v
    Event Detail   Szobafoglalás
         │              │
         └────┬─────────┘
              v
      Profil / Foglalások
```

### B. Admin Folyamatok

```
┌─────────────────┐
│  Admin User     │
└────────┬────────┘
         │
    ┌────┴─────────────┐
    │                  │
    v                  v
Event Mgmt         Room Mgmt
(CRUD)            (CRUD)
    │                  │
    ├──Create          ├──Create
    ├──Edit            ├──Edit
    ├──Delete          ├──Delete
    └──List            └──List
```

## 3. Adatmodell

### 3.1 Entitás-Kapcsolat Diagram (ERD)

```
                        ┌──────────────┐
                        │     User     │
                        ├──────────────┤
                        │ id (PK)      │
                        │ name         │
                        │ email (UK)   │
                        │ password     │
                        │ phone        │
                        │ address      │
                        │ role (ENUM)  │
                        │ created_at   │
                        └──────┬───────┘
                    1          │          N
                    ┌──────────┼──────────┐
                    │          │          │
            1:N     │          │     1:N  │
         ┌──────────┤          │          ├──────────┐
         │          │          │          │          │
         v          v          v          v          v
    ┌────────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌──────────┐
    │ Event  │ │Booking  │ │Favorite│ │Audit │ │Permission│
    ├────────┤ ├─────────┤ ├────────┤ ├──────┤ ├──────────┤
    │ id(PK) │ │ id(PK)  │ │event_id│ │      │ │ id(PK)   │
    │ title  │ │user_id  │ │user_id │ │action│ │name(UK)  │
    │ descr. │ │room_id  │ └────────┘ └──────┘ └──────────┘
    │ start_at│ │check_in │
    │ price  │ │check_out│     M:N
    │ venue_ │ │status   │   ┌────────────┐
    │ id(FK) │ │total_pr │   │RolePermission│
    └────────┘ │created  │   └────────────┘
       N       └─────────┘
       │          N
       │       ┌──────────┐     N
       │   1:N │Reservation│ 1:N
       │   └────────────────┘
       │        │
       │        │ venue_id
       │        │ (optional FK)
       │   ┌────┴──────┐
       │   │   Venue   │
       │   ├───────────┤
       │   │ id(PK)    │
       │   │ name(UK)  │
       │   │ address   │
       │   │ capacity  │
       │   └─────┬─────┘
       │         │
       │    1:N  │
       └─────────┤
               │
               v
           ┌────────────┐     N:N    ┌─────────────┐
           │   Room     │◄─────┼─────►│BookingService│
           ├────────────┤      │      ├─────────────┤
           │ id(PK)     │      │      │booking_id   │
           │room_number │      │      │service_id   │
           │capacity    │      │      │quantity     │
           │price_night │      │      └─────────────┘
           │status(ENUM)│      │            ▲
           │description │      │            │ N:1
           │venue_id(FK)│      │      ┌──────┴──────┐
           └────────────┘      │      │ExtraService │
                              │      ├─────────────┤
                              │      │id(PK)       │
                              │      │name         │
                              │      │price        │
                              │      │description  │
                              │      └─────────────┘
                              │
                              │
                          1:1  │
                         ┌─────┴──────┐
                         │Invoice     │
                         ├────────────┤
                         │booking_id(UK)
                         │total_amount│
                         │paid        │
                         │paid_at     │
                         └────────────┘
```

### 3.2 Kulcs Entitások

#### User (Felhasználó)
```sql
id INT PRIMARY KEY AUTO_INCREMENT
name VARCHAR(255) NOT NULL
email VARCHAR(255) UNIQUE NOT NULL
password VARCHAR(255) NOT NULL
phone VARCHAR(20)
address VARCHAR(500)
role ENUM('guest', 'receptionist', 'manager', 'admin') DEFAULT 'guest'
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### Event (Esemény)
```sql
id INT PRIMARY KEY AUTO_INCREMENT
title VARCHAR(255) NOT NULL
description TEXT
price DECIMAL(10,2)
start_at DATETIME
venue_id INT FOREIGN KEY REFERENCES venue(id)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### Room (Szoba)
```sql
id INT PRIMARY KEY AUTO_INCREMENT
venue_id INT FOREIGN KEY REFERENCES venue(id)
room_number VARCHAR(50) UNIQUE NOT NULL
capacity INT NOT NULL
price_per_night DECIMAL(10,2) NOT NULL
description TEXT
equipment VARCHAR(500)
status ENUM('available', 'occupied', 'maintenance', 'unavailable') DEFAULT 'available'
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### Booking (Foglalás)
```sql
id INT PRIMARY KEY AUTO_INCREMENT
user_id INT NOT NULL FOREIGN KEY REFERENCES user(id)
room_id INT NOT NULL FOREIGN KEY REFERENCES room(id)
check_in DATETIME NOT NULL
check_out DATETIME NOT NULL
guests_count INT NOT NULL
status ENUM('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled') DEFAULT 'pending'
total_price DECIMAL(10,2) DEFAULT 0
check_in_time DATETIME
check_out_time DATETIME
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## 4. Rendszer Funkciók

### 4.1 Esemény Kezelés (Event Management)
- Esemény listázása és keresése
- Esemény részleteinek megtekintése
- Foglalás az eseményre
- Kedvenc szervezés
- Kategóriázás

### 4.2 Szobafoglalás (Hotel Booking)
- Szobakeresés dátumtartomány alapján
- Szobafoglalás
- Foglalás módosítása
- Foglalás törlése
- Számla generálás
- Kiegészítő szolgáltatások (extra pillow, etc.)

### 4.3 Adminisztráció
- Szobák kezelése (CRUD)
- Felhasználók kezelése
- Foglalások nézete
- Audit log szekció

### 4.4 Authentikáció & Autorizáció
- Regisztráció
- Bejelentkezés (Session + JWT)
- Jelszó-alapú autentikáció
- Role-based access control (RBAC)
- Permission-based authorization

## 5. API Végpontok

### 5.1 Event API
```
GET  /                                    # Event listing
GET  /event/detail/<id>                   # Event details
GET  /api/events                          # REST API - all events
POST /event/new                           # Create event (admin)
POST /event/edit/<id>                     # Edit event (admin)
POST /event/delete/<id>                   # Delete event (admin)
```

### 5.2 Booking API
```
GET  /guest/search                        # Search available rooms
POST /guest/search                        # Execute search
GET  /guest/book/<room_id>                # Book room form
POST /guest/book/<room_id>                # Create booking
GET  /guest/bookings                      # User's bookings
GET  /guest/booking/<id>                  # Booking details
POST /guest/booking/<id>/edit             # Modify booking
POST /guest/booking/<id>/cancel           # Cancel booking
GET  /guest/booking/<id>/invoice          # Invoice view
```

### 5.3 Admin API
```
GET  /admin/rooms                         # Rooms list
GET  /admin/rooms/new                     # New room form
POST /admin/rooms/new                     # Create room
GET  /admin/rooms/<id>/edit               # Edit room form
POST /admin/rooms/<id>/edit               # Update room
POST /admin/rooms/<id>/delete             # Delete room
```

### 5.4 Auth API
```
GET  /register                            # Registration page
POST /register                            # Create user
GET  /login                               # Login page
POST /login                               # Authenticate
GET  /logout                              # Logout
GET  /profile                             # User profile
POST /profile                             # Update profile
```

## 6. Kódszerkezet

```
beadando_nagyzh/
├── WebApp/
│   ├── __init__.py               # Flask app initialization, Flasgger setup
│   ├── routes.py                 # Main routes (events, auth)
│   ├── models/
│   │   ├── __init__.py          # Model imports
│   │   ├── user.py              # User model
│   │   ├── event.py             # Event model
│   │   ├── room.py              # Room model
│   │   ├── booking.py           # Booking model
│   │   ├── venue.py             # Venue model
│   │   ├── category.py          # Category model
│   │   ├── reservation.py       # Reservation model
│   │   ├── permission.py        # Permission model
│   │   ├── extra_service.py     # ExtraService model
│   │   ├── booking_service.py   # BookingService model
│   │   ├── invoice.py           # Invoice model
│   │   └── audit_log.py         # AuditLog model
│   ├── forms/
│   │   ├── authforms.py         # Auth forms
│   │   ├── eventform.py         # Event form
│   │   ├── categoryform.py      # Category form
│   │   ├── reservationform.py   # Reservation form
│   │   ├── venueform.py         # Venue form
│   │   └── eventtimeform.py     # EventTime form
│   ├── blueprints/
│   │   ├── __init__.py          # Blueprint exports
│   │   ├── guest.py             # Guest blueprint (booking)
│   │   └── admin.py             # Admin blueprint
│   ├── managers/
│   │   └── eventmanager.py      # Business logic for events
│   ├── api/
│   │   └── swagger_config.py    # OpenAPI/Swagger config
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── index.html           # Event listing
│   │   ├── event/               # Event templates
│   │   ├── auth/                # Auth templates
│   │   ├── guest/               # Booking templates
│   │   └── admin/               # Admin templates
│   └── static/
│       └── img/                 # Static images
├── migrations/                  # Alembic migrations
├── tests/                       # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── test_models.py          # Model unit tests
│   ├── test_routes.py          # Route tests
│   └── test_integration.py     # Integration tests
├── app.py                      # Application entry point
├── config.py                   # Configuration
├── init_db.py                  # Database initialization
├── init_hotel_system.py        # Hotel schema setup
├── requirements.txt            # Dependencies
├── COMPETENCY_COMPLIANCE.md    # Kompetencia megfelelés
├── TESTING.md                  # Testing guide
└── README.md                   # Project documentation
```

## 7. Biztonsági Jellemzők

### 7.1 Authentikáció
- **Password Hashing**: werkzeug.security (PBKDF2)
- **Session Management**: Flask-Login
- **Token-Based Auth**: Flask-JWT-Extended
- **CSRF Protection**: WTForms CSRF tokens

### 7.2 Autorizáció
- **Role-Based Access Control (RBAC)**
  - guest (vendég - alapértelmezett)
  - receptionist (recepciós)
  - manager (menedzser)
  - admin (rendszergazda)
- **Permission-Based Authorization**
  - Fine-grained permissions
  - Role-permission mapping

### 7.3 Audit
- **Audit Logging**: Minden fontosabb művelet naplózva
- **Change Tracking**: Módosítási idők
- **User Attribution**: Ki végzett mit

## 8. Teljesítmény Jellemzők

### 8.1 Adatbázis Optimizálás
- **Indexes**: Felhasználó email, szoba szám, foglalás status
- **Foreign Keys**: Referencia integritás
- **Cascade Delete**: Adatok konzisztenciája

### 8.2 Lekérdezés Optimizálás
- **Pagination**: Összes listázás lapozottan
- **Relationship Loading**: back_populates, lazy loading
- **Query Filtering**: Szűrés dátum, kategória alapján

### 8.3 Sebezhetőség Elleni Védelmi
- **SQL Injection**: SQLAlchemy ORM
- **XSS Protection**: Jinja2 auto-escaping
- **CSRF**: WTForms CSRF tokens
- **Input Validation**: WTForms validators

## 9. Deployment Szcenáriók

### 9.1 Development
```bash
python app.py
# SQLite database: hotelbooking.db
# Debug mode: True
```

### 9.2 Production (MySQL)
```bash
python app.py
# MySQL connection: config.ini alapján
# Debug mode: False
# WSGI server: Gunicorn/uWSGI
```

### 9.3 Testing
```bash
pytest tests/
# SQLite :memory: database
# Fixtures: Test data automatically
```

## 10. Bővítési Pontok

- **Payment Integration**: Stripe/PayPal
- **Email Notifications**: Booking confirmations
- **SMS Alerts**: Check-in reminders
- **Analytics Dashboard**: Booking trends
- **Rating System**: Event/room reviews
- **Multi-language**: i18n support
- **Mobile App**: React Native frontend

---

**Verzió:** 1.0  
**Frissítés dátuma:** 2026-05-17  
**Készítette:** Development Team
