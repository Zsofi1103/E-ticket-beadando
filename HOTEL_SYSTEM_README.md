# Hotel Booking System - Implementáció Terv

## ✅ Teljesített

### Adatbázis Modellek
- ✅ Room (szoba kezelés)
- ✅ Booking (foglalások)
- ✅ ExtraService (extra szolgáltatások)
- ✅ BookingService (N:N kapcsolat)
- ✅ Invoice (számlázás)
- ✅ Permission & RolePermission (jogosultságok)
- ✅ AuditLog (naplózás)
- ✅ User frissítés (phone, address, új role-ok)

### Adatbázis
- ✅ SQL táblákat létrehozva
- ✅ Minta adatok betöltve:
  - 6 szoba
  - 7 extra szolgáltatás
  - 10 jogosultság
  - 4 role (guest, receptionist, manager, admin)

## 🚧 Implementálandó

### 1. Routes Szervezés (Priority 1)
- [ ] Blueprint-ekre bontás:
  - auth_bp: bejelentkezés, regisztráció
  - guest_bp: vendég funkciók (szobakeresés, foglalás)
  - receptionist_bp: recepciós funkciók
  - admin_bp: admin funkcionalitás
  - api_bp: REST API

### 2. Vendég Funkciók (Priority 2)
- [ ] Szobakeresés oldal (dátum, vendégszám)
- [ ] Foglalási folyamat
- [ ] Saját foglalások listája
- [ ] Foglalás módosítása
- [ ] Foglalás lemondása
- [ ] Számla letöltés (PDF)

### 3. Recepciós Funkciók (Priority 3)
- [ ] Foglalások dashboard
- [ ] Check-in/Check-out kezelés
- [ ] Extra szolgáltatások hozzáadása
- [ ] Status módosítás

### 4. Admin Funkciók (Priority 4)
- [ ] Szobakezelés (CRUD)
- [ ] Felhasználókezelés
- [ ] Extra szolgáltatások kezelés
- [ ] Audit napló megtekintése

### 5. Technikai Fejlesztések
- [ ] PDF számla generálás (xhtml2pdf)
- [ ] REST API endpoints
- [ ] RBAC dekorátorok
- [ ] Ütközés-detektálás
- [ ] Tesztek

## Fájlszerkezet

```
WebApp/
├── blueprints/
│   ├── auth.py          # Bejelentkezés, regisztráció
│   ├── guest.py         # Vendég funkciók
│   ├── receptionist.py  # Recepciós funkciók
│   ├── admin.py         # Admin funkciók
│   └── api.py           # REST API
├── models/
│   ├── room.py          ✅
│   ├── booking.py       ✅
│   ├── extra_service.py ✅
│   ├── invoice.py       ✅
│   ├── audit_log.py     ✅
│   └── permission.py    ✅
├── services/
│   ├── booking_service.py    # Foglalás logika
│   ├── invoice_service.py    # Számla generálás
│   └── audit_service.py      # Naplózás
├── forms/
│   ├── booking_form.py       # Foglalási forma
│   ├── search_form.py        # Szobakeresési forma
│   └── service_form.py       # Szolgáltatás forma
├── templates/
│   ├── guest/
│   │   ├── search_rooms.html      # Szobakeresés
│   │   ├── booking.html           # Foglalási oldal
│   │   ├── my_bookings.html       # Saját foglalások
│   │   └── invoice.html           # Számla nézet
│   ├── receptionist/
│   │   ├── dashboard.html         # Recepciós dashboard
│   │   └── manage_booking.html    # Foglalás kezelés
│   └── admin/
│       ├── rooms.html             # Szobakezelés
│       ├── users.html             # Felhasználókezelés
│       └── audit_logs.html        # Audit napló
└── static/
    ├── css/
    └── img/
```

## Függőségek
- Flask 3.1.1
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-JWT-Extended 4.7.1
- xhtml2pdf 0.2.17 (PDF generálás)
- reportlab 4.5.0

## Telepítés & Indítás

```bash
# 1. Függőségek telepítése
pip install -r requirements.txt

# 2. Adatbázis inicializálása
python init_hotel_system.py

# 3. App indítása
python app.py
```

## API Endpoints (Terv)

### Szobakezelés
- GET /api/v1/rooms - Szobák listája
- GET /api/v1/rooms/{id} - Szoba adatai
- POST /api/v1/rooms - Új szoba (admin)
- PUT /api/v1/rooms/{id} - Szoba módosítása (admin)
- DELETE /api/v1/rooms/{id} - Szoba törlése (admin)

### Foglalások
- GET /api/v1/bookings - Foglalások listája
- POST /api/v1/bookings - Új foglalás
- GET /api/v1/bookings/{id} - Foglalás adatai
- PUT /api/v1/bookings/{id} - Foglalás módosítása
- DELETE /api/v1/bookings/{id} - Foglalás lemondása

### Extra Szolgáltatások
- GET /api/v1/services - Szolgáltatások listája
- POST /api/v1/services - Új szolgáltatás (admin)

## Fejlesztési Ütemezés

1. **1. Fázis**: Routes és Blueprint-ek (ma)
2. **2. Fázis**: Alapvető UI (szobakeresés, foglalás)
3. **3. Fázis**: Recepciós funkciók
4. **4. Fázis**: Admin funkciók
5. **5. Fázis**: PDF és API finomítások
