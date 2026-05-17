# Event-Ticket + Hotel Booking System

Integrált esemény-foglalás és szobafoglalás alkalmazás Flask keretrendszerrel és SQLAlchemy ORM-mel.

**Status:** ✅ Production-ready (unit tesztek és API dokumentáció után)

## Projekt Áttekintés

Ez az alkalmazás két funkciót integrál:
- 🎫 **Event Management** - Eseménylefoglalás és kezelés
- 🏨 **Hotel Booking** - Szobafoglalás az esemény helyszínén

### Technológia Stack

| Komponens | Verzió | Leírás |
|-----------|--------|--------|
| **Python** | 3.14+ | Programozási nyelv |
| **Flask** | 3.1.2+ | Web keretrendszer |
| **SQLAlchemy** | 2.0.42+ | ORM |
| **Flask-SQLAlchemy** | 3.1.1+ | Flask integrációt |
| **MySQL** | 8.0+ | Production adatbázis |
| **SQLite** | - | Development/Test DB |
| **Alembic** | 1.16.4+ | Schema migrációk |
| **Flasgger** | 0.9.7+ | OpenAPI/Swagger doc |
| **pytest** | 7.4.3+ | Testing framework |
| **Bootstrap** | 5.3.0+ | Frontend UI |

## Gyors Indítás

### 1. Virtual Environment Létrehozása

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 2. Függőségek Telepítése

```bash
pip install -r requirements.txt
```

### 3. Adatbázis Beállítása

#### Development (SQLite)
```bash
python init_db.py
```

#### Production (MySQL)
```bash
# config.ini szerkesztése MySQL adatokkal
python init_hotel_system.py
```

### 4. Alkalmazás Indítása

```bash
python app.py
# Látogass meg: http://localhost:5000
```

## Projekt Szerkezete

```
├── app.py                      # Belépési pont
├── config.py                   # Konfigurációk
├── requirements.txt            # Python függőségek
├── config.ini                  # Adatbázis config (git ignored)
├── WebApp/
│   ├── __init__.py            # Flask app, Flasgger setup
│   ├── routes.py              # Fő útvonalak
│   ├── models/                # Adatbázis modellek
│   ├── forms/                 # WTForms validáció
│   ├── blueprints/            # Flask blueprints
│   │   ├── guest.py           # Szobafoglalás
│   │   └── admin.py           # Adminisztráció
│   ├── managers/              # Üzleti logika
│   ├── api/                   # API config, versioning
│   ├── templates/             # Jinja2 sablonok
│   └── static/                # CSS/JS/képek
├── tests/                     # pytest tesztek
├── migrations/                # Alembic schema verziókezelés
├── COMPETENCY_COMPLIANCE.md   # Kompetencia-megfelelés
├── ARCHITECTURE.md            # Rendszerarchitektúra
├── TESTING.md                 # Tesztelési útmutató
└── SCRIPTS_DESCRIPTIONS.md    # Scriptok dokumentációja
```

## Kompatibilitás

✅ **Python 3.14+ kompatibilis** 
- Beépített workaround az `ast.Str` eltávolításához
- Flask 3.1.2+, Werkzeug 3.1.0+ szükséges

## Funkciók

### Felhasználó Funkciók
- 📝 Regisztráció és bejelentkezés
- 🎫 Esemény-foglalás
- ❤️ Kedvenc események
- 🛏️ Szobafoglalás
- 📋 Foglalási előzmények
- 💰 Számlázás

### Admin Funkciók
- 📅 Esemény kezelés (CRUD)
- 🏨 Szoba kezelés (CRUD)
- 👥 Felhasználó kezelés
- 📊 Foglalási statisztika
- 📋 Audit naplók

## API Dokumentáció

### OpenAPI/Swagger

Az API dokumentáció elérhető:
- **Swagger UI**: `http://localhost:5000/api/docs`
- **OpenAPI JSON**: `http://localhost:5000/apispec.json`

### API Végpontok

#### Események
```
GET  /api/events              # Összes esemény
GET  /event/detail/<id>       # Esemény részletei
```

#### Szobafoglalás
```
GET  /guest/search            # Szoba keresés
POST /guest/book/<room_id>    # Szoba foglalása
GET  /guest/bookings          # Felhasználó foglalásai
```

#### Admin
```
GET  /admin/rooms             # Szobák listázása
POST /admin/rooms/new         # Új szoba
PUT  /admin/rooms/<id>/edit   # Szoba módosítása
DELETE /admin/rooms/<id>      # Szoba törlése
```

## Tesztelés

### Tesztek Futtatása

```bash
# Összes teszt
pytest

# Kód lefedettség
pytest --cov=WebApp tests/

# HTML-ben megjelenítve
pytest --cov=WebApp --cov-report=html tests/
```

### Teszt Kategóriák

- **Unit Tests** (`test_models.py`) - Modell tesztek
- **Route Tests** (`test_routes.py`) - API végpont tesztek
- **Integration Tests** (`test_integration.py`) - Workflow tesztek

Lásd: [TESTING.md](TESTING.md) - Részletes tesztelési útmutató

## Biztonsági Jellemzők

✅ **Authentikáció**
- Password hashing (PBKDF2)
- Session-based és JWT authentication
- CSRF protection

✅ **Autorizáció**
- Role-based access control (RBAC)
- Permission-based authorization
- Admin-only endpoints

✅ **Adatvédelem**
- SQL injection védelem (SQLAlchemy ORM)
- XSS védelem (Jinja2 auto-escaping)
- Input validation (WTForms)

✅ **Audit**
- Összes műveletnaplózás
- User attribution
- Módosítási időkövetés

## Kompetencia Megfelelés

Az alkalmazás megfelel az alábbi informatikai szak kompetencia-követelményeknek:

✅ Adatbázis kezelés (ORM, SQLAlchemy)
✅ Architektúra rétegek (Layered architecture)
✅ Authentikáció és autorizáció (RBAC)
✅ Hálózati kommunikáció (HTTP, REST API)
✅ OpenAPI/Swagger dokumentáció
✅ Unit tesztelés (pytest)
✅ Programozási módszertanok (MVC, SOLID)

Teljes dokumentáció: [COMPETENCY_COMPLIANCE.md](COMPETENCY_COMPLIANCE.md)

## Architekturális Dokumentáció

Részletes rendszerarchitektúra, adatmodell, és komponens diagrammok:
[ARCHITECTURE.md](ARCHITECTURE.md)

## Környezeti Beállítások

### config.ini (MySQL Production)

```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = event_hotel
```

### Environment Variables

```bash
# Development
set FLASK_ENV=development
set FLASK_DEBUG=1

# Production
set FLASK_ENV=production
set SECRET_KEY=your-secret-key-here
```

## Fejlesztési Útmutató

### Új Modell Hozzáadása

```python
# WebApp/models/new_model.py
from WebApp import db

class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
```

### Új Route Hozzáadása

```python
# WebApp/routes.py vagy WebApp/blueprints/blueprint.py
@app.route('/new-endpoint', methods=['GET', 'POST'])
def new_endpoint():
    """OpenAPI dokumentáció"""
    return render_template('new_endpoint.html')
```

### Tesztek Írása

```python
# tests/test_new_feature.py
def test_something(authenticated_client, init_database):
    response = authenticated_client.get('/endpoint')
    assert response.status_code == 200
```

## Ismert Problémák

- **Python 3.14 kompatibilitás**: `ast.Str` eltávolítás miatt workaround szükséges
- **MySQL timeout**: Hosszú foglaláslisták letöltése lassú lehet

## Jövőbeli Fejlesztések

- 💳 Payment integration (Stripe)
- 📧 Email notifications
- 📱 Mobile app
- ⭐ Rating system
- 🌐 Multi-language support
- 📊 Advanced analytics dashboard

## Hozzájárulás

1. Fork a projektet
2. Hozz létre feature branch (`git checkout -b feature/amazing-feature`)
3. Commit az alkalmazás (`git commit -m 'Add amazing feature'`)
4. Push a branch-hez (`git push origin feature/amazing-feature`)
5. Nyiss egy Pull Request

## Licenc

MIT License - Lásd LICENSE fájlt

## Támogatás

Kérdések vagy problémák? Nyiss GitHub issue-t.

---

**Verzió:** 1.0.0  
**Utolsó frissítés:** 2026-05-17  
**Python kompatibilitás:** 3.14+  
**Status:** ✅ Production-ready
