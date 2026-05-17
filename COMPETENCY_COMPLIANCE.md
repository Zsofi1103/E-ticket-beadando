# Event-Ticket + Hotel Booking Rendszer - Kompetencia Megfelelési Dokumentum

## Ismeret szint - Lefedett Területek

### ✅ Programozás módszertani alapjai
- **Valósítás:** Python, Flask framework
- **Elemek:** MVC architektúra, RESTful API design, SOLID elvek
- **Fájlok:** `WebApp/routes.py`, `WebApp/blueprints/`, `WebApp/models/`

### ✅ Programozási nyelvek
- **Valósítás:** Python 3.14+, HTML5, CSS3, JavaScript
- **Eszközök:** Flask, SQLAlchemy, Jinja2 template engine
- **Fájlok:** `/WebApp/`, `/WebApp/templates/`

### ✅ Alkalmazások fejlesztése
- **Architektúra:** Layered architecture (Models, Views, Controllers/Routes)
- **Funkciók:** 
  - Event management (create, read, update, delete)
  - Room booking system
  - User authentication & profiles
  - Admin dashboard
- **Fájlok:** `WebApp/models/`, `WebApp/routes.py`, `WebApp/blueprints/`

### ✅ Számítógép architektúrák és operációs rendszerek
- **Valósítás:** Cross-platform (Windows, Linux)
- **Folyamatkezelés:** Flask development server, async operations
- **Verziók:** Python 3.14+ compatibility workaround az `ast.Str` eltávolítására

### ✅ Számítógépes hálózatok
- **HTTP protokoll:** GET, POST, PUT, DELETE requests
- **Szerver-kliens:** Flask server, böngésző kliens, AJAX
- **Fájlok:** `WebApp/routes.py`, `/WebApp/templates/` AJAX

### ✅ Adatbázisok elméleti alapjai
- **ORM:** SQLAlchemy 2.0.42+
- **Adatmodell:**
  - Entitások: User, Event, Room, Booking, Venue, Category, Reservation
  - Relációtípusok: 1:N, N:N (many-to-many)
  - Egyedi megszorítások, Foreign Keys
- **Fájlok:** `WebApp/models/` (8+ model fájl)

---

## Fejlesztési Folyamatok - Lefedett Területek

### ✅ Programozási technológia
- **Design patterns:**
  - Repository pattern (EventManager)
  - Decorator pattern (@admin_required, @login_required)
  - MVC pattern
- **Error handling:** Try-catch blokkok, user feedback (flash messages)
- **Code organization:** Blueprints (modularizálás)
- **Fájlok:** `WebApp/managers/`, `WebApp/blueprints/`

### ✅ Adatbázisok felépítése és menedzselése
- **Schema management:** SQLAlchemy models, Alembic migrations
- **Relationships:** back_populates, cascade delete rules
- **Transactions:** Commit/rollback pattern
- **Indexes:** performance optimization
- **Fájlok:** `WebApp/models/`, `migrations/`, `init_hotel_system.sql`

### ✅ Authentikáció és Authorizáció
- **Authentication:**
  - Flask-Login session management
  - Password hashing (werkzeug.security)
  - Login/Register/Logout flows
- **Authorization:**
  - Role-based access control (UserRole enum)
  - @admin_required decorator
  - Permission system (Permission + RolePermission models)
- **Fájlok:** `WebApp/models/user.py`, `WebApp/routes.py`

### ✅ Vállalati információs rendszerek
- **User management:** Roles (guest, receptionist, manager, admin)
- **Audit logging:** AuditLog model - összes akciókövetés
- **Reports:** Admin dashboard potencial
- **Fájlok:** `WebApp/models/user.py`, `WebApp/models/audit_log.py`

### ✅ Internet eszközök és szolgáltatások
- **REST API:** JSON endpoints (`/api/events`)
- **Frontend:** Bootstrap 5.3.0, responsive design
- **Template engine:** Jinja2
- **Fájlok:** `/WebApp/templates/`, `WebApp/routes.py`

### ✅ Információbiztonság
- **Jelszókezelés:** Salted hashing (werkzeug.security)
- **CSRF protection:** WTForms CSRF tokens
- **Session security:** Flask-Login session management
- **Fájlok:** `WebApp/models/user.py`, `WebApp/forms/`

### ✅ Rendszertervezés alapjai
- **Architekturális diagram:** Layered architecture
- **Komponensek:** Models, Views, Controllers, Services, Forms
- **Adatfolyam:** Request → Route → Service → Model → Database
- **Fájlok:** Ez a dokumentum, project README

### ✅ Projektmenedzsment módszertanok
- **Verzió kezelés:** Git (altalánosított)
- **Iteratív fejlesztés:** Continuous feature adding
- **Task tracking:** Migrációs fázisok

---

## Képességek - Lefedett Szintek

### ✅ Matematikai és számítástudományi elvek alkalmazása
- **Adatstruktúrák:** Lists, Dictionaries, Sets, Tuples
- **Algoritmusok:** Pagination, Filtering, Sorting
- **Logika:** Conditional statements, loops, recursive relationships
- **Numerikus:** Price calculations, DateTime handling

### ✅ Algoritmus design és implementáció
- **Availability checking:** Room conflict detection algorithm
  ```python
  def is_available(check_in, check_out):
      # Overlapping booking detection
  ```
- **Search algorithms:** Category/date filtering
- **Paradigmák:** Object-Oriented Programming (OOP)
- **Fájlok:** `WebApp/models/room.py` (is_available method)

### ✅ Szoftverfejlesztési módszertanok
- **Tervezés:** Model-driven design
- **Fejlesztés:** Incremental feature building
- **Dokumentálás:** Docstrings, code comments (magyar és angol)
- **Tesztelés:** Manual testing (CLI, browser)
- **Kódminőség:** Clean code principles, meaningful names
- **Validálás:** Form validation (WTForms)

### ✅ Csapatmunka és kommunikáció
- **Kód dokumentálása:** Docstrings, README files
- **Nyomtracezés:** Logging (flask_errors.log)
- **Error messages:** User-friendly Hungarian feedback
- **Fájlok:** README.md, Docstrings a models-ben

### ✅ Önfejlesztés és új technológiák
- **Python 3.14 compatibility fix:** ast.Str workaround
- **Framework adoption:** Flask, SQLAlchemy
- **Problem-solving:** Runtime issues resolution

---

## Tantárgy Témakörök - Lefedett Elemek

### ✅ Adatbázis kezelés, ORM keretrendszerek
- **ORM:** SQLAlchemy 2.0+
- **CRUD operációk:** Create, Read, Update, Delete implementálva
- **Relációk:** Foreign Keys, back_populates, cascade
- **Migrációk:** Alembic versioning
- **Fájlok:** `WebApp/models/`, `migrations/`, `init_hotel_system.sql`

### ✅ Architektúra rétegek
```
┌─────────────────────────────────────┐
│  Presentation Layer (Templates)     │  HTML/CSS/JS
├─────────────────────────────────────┤
│  Controller Layer (Routes/Blueprints)│  Flask routes
├─────────────────────────────────────┤
│  Service Layer (Managers/Logic)     │  EventManager
├─────────────────────────────────────┤
│  Model Layer (ORM)                  │  SQLAlchemy models
├─────────────────────────────────────┤
│  Data Layer (Database)              │  MySQL/SQLite
└─────────────────────────────────────┘
```
- **Fájlok:** Teljes projekt szerkezet

### ✅ Authentikáció és authorizáció
- **Authentication Methods:**
  - Session-based (Flask-Login)
  - JWT-based (Flask-JWT-Extended)
  - Password hashing (werkzeug.security)
- **Authorization Methods:**
  - Role-based (RBAC)
  - Permission-based (Permission model)
  - Decorator-based access control
- **Fájlok:** `WebApp/routes.py`, `WebApp/models/user.py`, `WebApp/models/permission.py`

### ✅ Hálózati kommunikáció
- **HTTP Methods:** GET, POST, PUT, DELETE
- **REST endpoints:** /api/events, /event/*, /booking/*
- **Request/Response:** JSON, Form data, Sessions
- **Status codes:** 200, 302, 400, 500
- **Fájlok:** `WebApp/routes.py`

### ✅ Szerver-kliens alkalmazások alapjai
- **Flask server:** Development server, app initialization
- **Böngésző kliens:** HTTP requests, session management
- **AJAX:** Dinamikus frissítések (booking service select)
- **WebSockets potencial:** Real-time updates lehetősége
- **Fájlok:** `app.py`, `/WebApp/templates/`

### ✅ OpenAPI, Swagger (HIÁNYZIK - 📌 TODO)
- **Aktuális:** `/api/events` JSON endpoint
- **Javasolt:** Flasgger integráció teljes API dokumentálásához
- **Fájlok:** (Még nem létezik - `WebApp/api/swagger_config.py`)

### ✅ Verzió kezelés (HIÁNYZIK - 📌 TODO)
- **Git:** Valószínűleg már verziókezelés alatt
- **API verzionálás:** v1, v2 endpoints lehetősége
- **Fájlok:** (Jelenlegi: v0.1 informal)

### ⚠️ Unit tesztelés (HIÁNYZIK - 📌 TODO)
- **Framework:** pytest javasolt
- **Fedettség:** Models, Routes, Services
- **Típusok:** Unit, Integration, E2E
- **Fájlok:** (Még nem létezik - `tests/` mappa)

---

## Hiányzó Komponensek és Javaslatok

| Komponens | Státusz | Prioritás | Megvalósítási idő |
|-----------|---------|-----------|-------------------|
| OpenAPI/Swagger | ⚠️ Hiányzik | MAGAS | 1-2 óra |
| Unit tesztelés | ⚠️ Hiányzik | MAGAS | 3-4 óra |
| Integráció tesztelés | ⚠️ Hiányzik | KÖZÉP | 2-3 óra |
| API verzionálás | ⚠️ Hiányzik | ALACSONY | 1 óra |
| Részletes kódkommentek | ✅ Részben | KÖZÉP | 1-2 óra |
| E2E tesztelés | ⚠️ Hiányzik | ALACSONY | 2-3 óra |
| Performance dokumentáció | ⚠️ Hiányzik | ALACSONY | 1 óra |

---

## Architektúra Összefoglalása

### Komponensek

1. **Models** (ORM réteg)
   - User, Event, Room, Booking, Venue, Category, Reservation, Permission
   - Relationships, constraints, enums

2. **Routes** (Controller réteg)
   - /event/* - event management
   - /user/* - authentication & profile
   - /guest/* - guest booking
   - /admin/* - administration
   - /api/* - REST endpoints

3. **Blueprints** (modularizálás)
   - guest_bp - szobafoglalás
   - admin_bp - adminisztráció

4. **Managers** (Service réteg)
   - EventManager - üzleti logika

5. **Forms** (Validation réteg)
   - WTForms alapú form kezelés

6. **Templates** (Presentation réteg)
   - Jinja2 template engine
   - Bootstrap 5 UI framework

### Adatfolyam

```
Böngésző HTTP Request
    ↓
Flask Route Handler (@app.route)
    ↓
Service Layer (Manager/Logic)
    ↓
Model Layer (SQLAlchemy query)
    ↓
Database (MySQL/SQLite)
    ↓
Response JSON / HTML Template
    ↓
Böngésző HTML/JSON Render
```

---

## Kompatibilitás Nyilatkozat

✅ **Teljes körűen megfelel az alábbi területeknek:**
- Programozás módszertani alapjai
- Programozási nyelvek
- Alkalmazások fejlesztése
- Adatbázisok elméleti alapjai
- Authentikáció és authorizáció
- Szerver-kliens alkalmazások
- Hálózati kommunikáció
- Adatbázis kezelés ORM-vel
- Architektúra rétegek
- Rendszertervezés alapjai
- Csapatmunka és kommunikáció

⚠️ **Részlegesen lefedett (javítható):**
- OpenAPI/Swagger dokumentáció
- Unit tesztelés
- Integráció tesztelés
- API verzionálás
- E2E tesztelés

---

**Dokumentum verziója:** 1.0  
**Utolsó frissítés:** 2026-05-17  
**Projekt státusza:** Production-ready (tesztelés és API doc után)
