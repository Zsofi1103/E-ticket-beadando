#!/usr/bin/env python3
"""
Adatbázis feltöltés szép, reális adatokkal.

Ezt futtasd: python seed_database.py
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text

# Import Flask app
from WebApp import app, db
from WebApp.models.user import User, UserRole
from WebApp.models.category import Category
from WebApp.models.event import Event
from WebApp.models.event_time import EventTime
from WebApp.models.venue import Venue
from WebApp.models.room import Room, RoomStatus
from WebApp.models.booking import Booking, BookingStatus
from WebApp.models.extra_service import ExtraService
from WebApp.models.booking_service import BookingService
from WebApp.models.reservation import Reservation
from WebApp.models.invoice import Invoice


def ensure_schema():
    """Biztosítja, hogy a room tábla rendelkezik venue_id oszloppal"""
    try:
        # Ellenőrizze, hogy venue_id oszlop létezik-e
        result = db.session.execute(
            text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='room' AND COLUMN_NAME='venue_id'")
        )
        if result.fetchone():
            print("✅ room.venue_id oszlop már létezik")
            return
        
        # Ha nem létezik, add hozzá
        db.session.execute(text("""
            ALTER TABLE room ADD COLUMN venue_id INT,
            ADD FOREIGN KEY (venue_id) REFERENCES venue(id)
        """))
        db.session.commit()
        print("✅ room.venue_id oszlop hozzáadva")
    except Exception as e:
        print(f"⚠️ Schema ellenőrzés: {e}")


def clear_database():
    """Töröl minden adatot az adatbázisból"""
    print("\n🗑️ Adatbázis törlése...")
    db.drop_all()
    db.create_all()
    print("✅ Adatbázis visszaállítva")


def seed_users():
    """Felhasználók feltöltése"""
    print("\n👥 Felhasználók feltöltése...")
    
    users = [
        User(
            name='Admin Felhasználó',
            email='admin@example.com',
            role=UserRole.admin
        ),
        User(
            name='Szálloda Vezetője',
            email='manager@hotel.com',
            role=UserRole.manager
        ),
        User(
            name='Recepcióista',
            email='receptionist@hotel.com',
            role=UserRole.receptionist
        ),
        User(
            name='John Doe',
            email='john@example.com',
            role=UserRole.guest
        ),
        User(
            name='Jane Smith',
            email='jane@example.com',
            role=UserRole.guest
        ),
        User(
            name='Kovács Péter',
            email='peter@example.com',
            role=UserRole.guest
        ),
    ]
    
    for user in users:
        user.set_password('password123')
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ {len(users)} felhasználó feltöltve")
    return users


def seed_categories():
    """Eseménykategóriák feltöltése"""
    print("\n🏷️ Kategóriák feltöltése...")
    
    categories = [
        Category(name='Koncert'),
        Category(name='Konferencia'),
        Category(name='Sportesemény'),
        Category(name='Fesztivál'),
        Category(name='Workshop'),
        Category(name='Szabadtéri Előadás'),
        Category(name='Közösségi Esemény'),
    ]
    
    for cat in categories:
        db.session.add(cat)
    
    db.session.commit()
    print(f"✅ {len(categories)} kategória feltöltve")
    return categories


def seed_venues():
    """Helyszínek és szobák feltöltése"""
    print("\n🏨 Helyszínek és szobák feltöltése...")
    
    venues = []
    rooms_count = 0
    
    # Budapest Kongresszusi Központ
    venue1 = Venue(
        name='Budapest Kongresszusi Központ',
        address='Jagelló út 1-3, 1146 Budapest',
        capacity=5000
    )
    db.session.add(venue1)
    db.session.flush()
    
    # Szobák a helyszínhez
    rooms_v1 = [
        Room(venue_id=venue1.id, room_number='101', capacity=2, price_per_night=Decimal('15000'), 
             description='Két ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        Room(venue_id=venue1.id, room_number='102', capacity=2, price_per_night=Decimal('15000'), 
             description='Két ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        Room(venue_id=venue1.id, room_number='103', capacity=4, price_per_night=Decimal('25000'), 
             description='Családi szoba 2 hálótérrel', equipment='WiFi, AC, TV, minibar, konyha', status=RoomStatus.available),
        Room(venue_id=venue1.id, room_number='201', capacity=2, price_per_night=Decimal('18000'), 
             description='Prémium szoba erkéllyel', equipment='WiFi, AC, TV, minibar, jacuzzi', status=RoomStatus.available),
        Room(venue_id=venue1.id, room_number='301', capacity=1, price_per_night=Decimal('12000'), 
             description='Egyágyas szoba', equipment='WiFi, AC, TV', status=RoomStatus.available),
    ]
    
    for room in rooms_v1:
        db.session.add(room)
        rooms_count += 1
    
    venues.append(venue1)
    
    # Óbudai-sziget Fesztivál Helyszín
    venue2 = Venue(
        name='Óbudai-sziget Fesztivál Helyszín',
        address='Sziget, Budapest',
        capacity=100000
    )
    db.session.add(venue2)
    db.session.flush()
    
    rooms_v2 = [
        Room(venue_id=venue2.id, room_number='TENT-A01', capacity=2, price_per_night=Decimal('8000'), 
             description='Glamping sátor', equipment='Ágy, villanypróba', status=RoomStatus.available),
        Room(venue_id=venue2.id, room_number='TENT-A02', capacity=2, price_per_night=Decimal('8000'), 
             description='Glamping sátor', equipment='Ágy, villanypróba', status=RoomStatus.available),
        Room(venue_id=venue2.id, room_number='HOTEL-101', capacity=3, price_per_night=Decimal('20000'), 
             description='Közeli szálloda szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        Room(venue_id=venue2.id, room_number='HOTEL-102', capacity=2, price_per_night=Decimal('18000'), 
             description='Közeli szálloda szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
    ]
    
    for room in rooms_v2:
        db.session.add(room)
        rooms_count += 1
    
    venues.append(venue2)
    
    # Papp László Sportaréna
    venue3 = Venue(
        name='Papp László Sportaréna',
        address='Stefánia út 2, 1146 Budapest',
        capacity=12500
    )
    db.session.add(venue3)
    db.session.flush()
    
    rooms_v3 = [
        Room(venue_id=venue3.id, room_number='VIP-1', capacity=2, price_per_night=Decimal('30000'), 
             description='VIP szoba aréna kilátással', equipment='WiFi, AC, TV, jacuzzi, sauna', status=RoomStatus.available),
        Room(venue_id=venue3.id, room_number='VIP-2', capacity=2, price_per_night=Decimal('30000'), 
             description='VIP szoba aréna kilátással', equipment='WiFi, AC, TV, jacuzzi, sauna', status=RoomStatus.available),
        Room(venue_id=venue3.id, room_number='STANDARD-101', capacity=2, price_per_night=Decimal('16000'), 
             description='Standard szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        Room(venue_id=venue3.id, room_number='STANDARD-102', capacity=2, price_per_night=Decimal('16000'), 
             description='Standard szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
    ]
    
    for room in rooms_v3:
        db.session.add(room)
        rooms_count += 1
    
    venues.append(venue3)
    
    # Debrecen Nagycsarnok
    venue4 = Venue(
        name='Debrecen Nagycsarnok',
        address='Baltazár tér 10, 4026 Debrecen',
        capacity=8000
    )
    db.session.add(venue4)
    db.session.flush()
    
    rooms_v4 = [
        Room(venue_id=venue4.id, room_number='D-101', capacity=2, price_per_night=Decimal('12000'), 
             description='Két ágyas szoba', equipment='WiFi, AC, TV', status=RoomStatus.available),
        Room(venue_id=venue4.id, room_number='D-102', capacity=3, price_per_night=Decimal('16000'), 
             description='Három ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
    ]
    
    for room in rooms_v4:
        db.session.add(room)
        rooms_count += 1
    
    venues.append(venue4)
    
    db.session.commit()
    print(f"✅ {len(venues)} helyszín feltöltve, {rooms_count} szoba hozzáadva")
    return venues


def seed_events(categories, venues):
    """Események feltöltése"""
    print("\n🎫 Események feltöltése...")
    
    events = []
    now = datetime.now()
    
    events_data = [
        {
            'title': 'Python Developer Konferencia 2026',
            'description': 'Az év legnagyobb Python programozási konferenciája',
            'category_id': categories[1].id,  # Konferencia
            'venue_id': venues[0].id,  # Budapest Kongresszus
            'ticket_price': Decimal('15000'),
            'start': now + timedelta(days=30),
            'end': now + timedelta(days=32),
        },
        {
            'title': 'Rock Fesztivál',
            'description': 'Nyári rockzene fesztivál a legjobbakkal',
            'category_id': categories[3].id,  # Fesztivál
            'venue_id': venues[1].id,  # Sziget
            'ticket_price': Decimal('25000'),
            'start': now + timedelta(days=60),
            'end': now + timedelta(days=67),
        },
        {
            'title': 'Cristiano Ronaldo - Interklass Futsal',
            'description': 'Szupercsapat futsal mérkőzés',
            'category_id': categories[2].id,  # Sportesemény
            'venue_id': venues[2].id,  # Papp László
            'ticket_price': Decimal('8000'),
            'start': now + timedelta(days=45),
            'end': now + timedelta(days=45),
        },
        {
            'title': 'Opera Gálafellépés',
            'description': 'A világ legjobb énekesei előadása',
            'category_id': categories[5].id,  # Szabadtéri előadás
            'venue_id': venues[0].id,
            'ticket_price': Decimal('12000'),
            'start': now + timedelta(days=25),
            'end': now + timedelta(days=25),
        },
        {
            'title': 'Web Development Workshop',
            'description': 'Gyakorlati webfejlesztési képzés professzionális trénerekkel',
            'category_id': categories[4].id,  # Workshop
            'venue_id': venues[3].id,  # Debrecen
            'ticket_price': Decimal('18000'),
            'start': now + timedelta(days=20),
            'end': now + timedelta(days=22),
        },
        {
            'title': 'DevOps Masterclass',
            'description': 'Összetett DevOps tanfolyam gyakorlati feladatokkal',
            'category_id': categories[4].id,  # Workshop
            'venue_id': venues[0].id,
            'ticket_price': Decimal('22000'),
            'start': now + timedelta(days=50),
            'end': now + timedelta(days=52),
        },
        {
            'title': 'Budapest Jazz Night',
            'description': 'Az elmúlt évtizedek legjobbjai előadnak',
            'category_id': categories[0].id,  # Koncert
            'venue_id': venues[2].id,
            'ticket_price': Decimal('6000'),
            'start': now + timedelta(days=35),
            'end': now + timedelta(days=35),
        },
        {
            'title': 'Közösségi Piac Nap',
            'description': 'Helyi termelők és kézművesek bemutatkozása',
            'category_id': categories[6].id,  # Közösségi
            'venue_id': venues[1].id,
            'ticket_price': Decimal('0'),  # Ingyenes
            'start': now + timedelta(days=10),
            'end': now + timedelta(days=10),
        },
    ]
    
    for data in events_data:
        event = Event(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            venue_id=data['venue_id'],
            ticket_price=data['ticket_price'],
        )
        db.session.add(event)
        db.session.flush()
        
        # Adj hozzá eseménytartamokat
        current_time = data['start']
        while current_time <= data['end']:
            event_time = EventTime(
                event_id=event.id,
                start_at=current_time,
                end_at=current_time + timedelta(hours=4)
            )
            db.session.add(event_time)
            current_time += timedelta(days=1)
        
        events.append(event)
    
    db.session.commit()
    print(f"✅ {len(events)} esemény feltöltve")
    return events


def seed_extra_services():
    """Extra szolgáltatások feltöltése"""
    print("\n🎁 Extra szolgáltatások feltöltése...")
    
    services = [
        ExtraService(name='Parkolás', price=Decimal('3000')),
        ExtraService(name='Fürdőzselé', price=Decimal('2000')),
        ExtraService(name='Reggeli', price=Decimal('4500')),
        ExtraService(name='Késői kijelentkezés', price=Decimal('5000')),
        ExtraService(name='Szobaszervíz', price=Decimal('3000')),
        ExtraService(name='Gyermek ágy', price=Decimal('2500')),
        ExtraService(name='Pet tisztálkodás', price=Decimal('5000')),
    ]
    
    for service in services:
        db.session.add(service)
    
    db.session.commit()
    print(f"✅ {len(services)} extra szolgáltatás feltöltve")
    return services


def seed_bookings(venues, extra_services):
    """Foglalások feltöltése"""
    print("\n🛏️ Foglalások feltöltése...")
    
    users = User.query.filter_by(role=UserRole.guest).all()
    bookings = []
    now = datetime.now()
    
    # Foglalások különböző helyszínekhez
    for i, venue in enumerate(venues):
        rooms = Room.query.filter_by(venue_id=venue.id).limit(2).all()
        
        for j, room in enumerate(rooms):
            check_in = now + timedelta(days=15 + i*10 + j*2)
            check_out = check_in + timedelta(days=2)
            
            booking = Booking(
                user_id=users[i % len(users)].id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                nights=2,
                total_price=room.price_per_night * 2,
                status=BookingStatus.confirmed,
                special_requests=f'Szobaszervíz kérünk a szobához'
            )
            db.session.add(booking)
            db.session.flush()
            
            # Add 1-2 extra szolgáltatást
            for k in range(1, 3):
                if k < len(extra_services):
                    booking_service = BookingService(
                        booking_id=booking.id,
                        extra_service_id=extra_services[k].id,
                        quantity=1
                    )
                    db.session.add(booking_service)
            
            bookings.append(booking)
    
    db.session.commit()
    print(f"✅ {len(bookings)} foglalás feltöltve")
    return bookings


def seed_reservations(events):
    """Esemény foglalások feltöltése"""
    print("\n📋 Esemény foglalások feltöltése...")
    
    users = User.query.filter_by(role=UserRole.guest).all()
    reservations = []
    
    for i, event in enumerate(events[:4]):  # Csak az első 4 eseményre
        for j in range(1, min(4, len(users) + 1)):
            reservation = Reservation(
                user_id=users[j % len(users)].id,
                event_id=event.id,
                quantity=i % 3 + 1,  # 1-3 jegy
            )
            db.session.add(reservation)
            reservations.append(reservation)
    
    db.session.commit()
    print(f"✅ {len(reservations)} esemény foglalás feltöltve")
    return reservations


def seed_invoices(bookings):
    """Számlák feltöltése"""
    print("\n📄 Számlák feltöltése...")
    
    invoices = []
    now = datetime.now()
    
    for booking in bookings[:5]:  # Csak az első 5 foglaláshoz
        invoice = Invoice(
            booking_id=booking.id,
            invoice_number=f"INV-{now.year}-{booking.id:04d}",
            amount=booking.total_price,
            issued_date=now,
            due_date=now + timedelta(days=30),
            paid_date=now + timedelta(days=5),
            status='paid'
        )
        db.session.add(invoice)
        invoices.append(invoice)
    
    db.session.commit()
    print(f"✅ {len(invoices)} számla feltöltve")
    return invoices


def print_summary():
    """Összefoglalást nyomtat az adatbázisról"""
    print("\n" + "="*60)
    print("📊 ADATBÁZIS FELTÖLTÉSI ÖSSZEFOGLALÁS")
    print("="*60)
    
    print(f"👥 Felhasználók: {User.query.count()}")
    print(f"🏷️ Kategóriák: {Category.query.count()}")
    print(f"🏨 Helyszínek: {Venue.query.count()}")
    print(f"🛏️ Szobák: {Room.query.count()}")
    print(f"🎫 Események: {Event.query.count()}")
    print(f"📝 Eseménytartamok: {EventTime.query.count()}")
    print(f"🛏️ Szobafoglalások: {Booking.query.count()}")
    print(f"🎟️ Esemény foglalások: {Reservation.query.count()}")
    print(f"🎁 Extra szolgáltatások: {ExtraService.query.count()}")
    print(f"📄 Számlák: {Invoice.query.count()}")
    
    print("\n🔐 ADMIN BEJELENTKEZÉS")
    print("="*60)
    print("Email: admin@example.com")
    print("Jelszó: password123")
    print("="*60)
    
    print("\n👤 TEST FELHASZNÁLÓK")
    print("="*60)
    users = User.query.all()
    for user in users:
        print(f"{user.name} ({user.email}) - {user.role.value}")
    
    print("\n🌐 HELYSZÍNEK ÉS SZOBÁK")
    print("="*60)
    venues = Venue.query.all()
    for venue in venues:
        rooms_count = Room.query.filter_by(venue_id=venue.id).count()
        print(f"\n{venue.name}")
        print(f"  Szobák: {rooms_count}")
        rooms = Room.query.filter_by(venue_id=venue.id).limit(3).all()
        for room in rooms:
            print(f"    - {room.room_number}: {room.capacity} fő, {room.price_per_night} Ft/éj")
    
    print("\n🎫 ESEMÉNYEK")
    print("="*60)
    events = Event.query.all()
    for event in events:
        print(f"• {event.title}")
        print(f"  Helyszín: {event.venue.name}")
        print(f"  Kategória: {event.category.name}")
        print(f"  Jegy ár: {event.ticket_price} Ft")
    
    print("\n✅ Adatbázis feltöltés kész!\n")


def clear_database():
    """Töröl minden adatot az adatbázisból"""
    with app.app_context():
        print("\n🗑️ Adatbázis törlése...")
        db.drop_all()
        db.create_all()
        print("✅ Adatbázis visszaállítva")


def seed_users():
    """Felhasználók feltöltése"""
    with app.app_context():
        print("\n👥 Felhasználók feltöltése...")
        
        users = [
            User(
                name='Admin Felhasználó',
                email='admin@example.com',
                role=UserRole.admin
            ),
            User(
                name='Szálloda Vezetője',
                email='manager@hotel.com',
                role=UserRole.manager
            ),
            User(
                name='Recepcióista',
                email='receptionist@hotel.com',
                role=UserRole.receptionist
            ),
            User(
                name='John Doe',
                email='john@example.com',
                role=UserRole.guest
            ),
            User(
                name='Jane Smith',
                email='jane@example.com',
                role=UserRole.guest
            ),
            User(
                name='Kovács Péter',
                email='peter@example.com',
                role=UserRole.guest
            ),
        ]
        
        for user in users:
            user.set_password('password123')
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ {len(users)} felhasználó feltöltve")
        return users


def seed_categories():
    """Eseménykategóriák feltöltése"""
    with app.app_context():
        print("\n🏷️ Kategóriák feltöltése...")
        
        categories = [
            Category(name='Koncert'),
            Category(name='Konferencia'),
            Category(name='Sportesemény'),
            Category(name='Fesztivál'),
            Category(name='Workshop'),
            Category(name='Szabadtéri Előadás'),
            Category(name='Közösségi Esemény'),
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        print(f"✅ {len(categories)} kategória feltöltve")
        return categories


def seed_venues():
    """Helyszínek és szobák feltöltése"""
    with app.app_context():
        print("\n🏨 Helyszínek és szobák feltöltése...")
        
        venues = []
        rooms_count = 0
        
        # Budapest Kongresszusi Központ
        venue1 = Venue(
            name='Budapest Kongresszusi Központ',
            address='Jagelló út 1-3, 1146 Budapest',
            capacity=5000
        )
        db.session.add(venue1)
        db.session.flush()
        
        # Szobák a helyszínhez
        rooms_v1 = [
            Room(venue_id=venue1.id, room_number='101', capacity=2, price_per_night=Decimal('15000'), 
                 description='Két ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
            Room(venue_id=venue1.id, room_number='102', capacity=2, price_per_night=Decimal('15000'), 
                 description='Két ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
            Room(venue_id=venue1.id, room_number='103', capacity=4, price_per_night=Decimal('25000'), 
                 description='Családi szoba 2 hálótérrel', equipment='WiFi, AC, TV, minibar, konyha', status=RoomStatus.available),
            Room(venue_id=venue1.id, room_number='201', capacity=2, price_per_night=Decimal('18000'), 
                 description='Prémium szoba erkéllyel', equipment='WiFi, AC, TV, minibar, jacuzzi', status=RoomStatus.available),
            Room(venue_id=venue1.id, room_number='301', capacity=1, price_per_night=Decimal('12000'), 
                 description='Egyágyas szoba', equipment='WiFi, AC, TV', status=RoomStatus.available),
        ]
        
        for room in rooms_v1:
            db.session.add(room)
            rooms_count += 1
        
        venues.append(venue1)
        
        # Óbudai-sziget Fesztivál Helyszín
        venue2 = Venue(
            name='Óbudai-sziget Fesztivál Helyszín',
            address='Sziget, Budapest',
            capacity=100000
        )
        db.session.add(venue2)
        db.session.flush()
        
        rooms_v2 = [
            Room(venue_id=venue2.id, room_number='TENT-A01', capacity=2, price_per_night=Decimal('8000'), 
                 description='Glamping sátor', equipment='Ágy, villanypróba', status=RoomStatus.available),
            Room(venue_id=venue2.id, room_number='TENT-A02', capacity=2, price_per_night=Decimal('8000'), 
                 description='Glamping sátor', equipment='Ágy, villanypróba', status=RoomStatus.available),
            Room(venue_id=venue2.id, room_number='HOTEL-101', capacity=3, price_per_night=Decimal('20000'), 
                 description='Közeli szálloda szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
            Room(venue_id=venue2.id, room_number='HOTEL-102', capacity=2, price_per_night=Decimal('18000'), 
                 description='Közeli szálloda szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        ]
        
        for room in rooms_v2:
            db.session.add(room)
            rooms_count += 1
        
        venues.append(venue2)
        
        # Papp László Sportaréna
        venue3 = Venue(
            name='Papp László Sportaréna',
            address='Stefánia út 2, 1146 Budapest',
            capacity=12500
        )
        db.session.add(venue3)
        db.session.flush()
        
        rooms_v3 = [
            Room(venue_id=venue3.id, room_number='VIP-1', capacity=2, price_per_night=Decimal('30000'), 
                 description='VIP szoba aréna kilátással', equipment='WiFi, AC, TV, jacuzzi, sauna', status=RoomStatus.available),
            Room(venue_id=venue3.id, room_number='VIP-2', capacity=2, price_per_night=Decimal('30000'), 
                 description='VIP szoba aréna kilátással', equipment='WiFi, AC, TV, jacuzzi, sauna', status=RoomStatus.available),
            Room(venue_id=venue3.id, room_number='STANDARD-101', capacity=2, price_per_night=Decimal('16000'), 
                 description='Standard szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
            Room(venue_id=venue3.id, room_number='STANDARD-102', capacity=2, price_per_night=Decimal('16000'), 
                 description='Standard szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        ]
        
        for room in rooms_v3:
            db.session.add(room)
            rooms_count += 1
        
        venues.append(venue3)
        
        # Debrecen Nagycsarnok
        venue4 = Venue(
            name='Debrecen Nagycsarnok',
            address='Baltazár tér 10, 4026 Debrecen',
            capacity=8000
        )
        db.session.add(venue4)
        db.session.flush()
        
        rooms_v4 = [
            Room(venue_id=venue4.id, room_number='D-101', capacity=2, price_per_night=Decimal('12000'), 
                 description='Két ágyas szoba', equipment='WiFi, AC, TV', status=RoomStatus.available),
            Room(venue_id=venue4.id, room_number='D-102', capacity=3, price_per_night=Decimal('16000'), 
                 description='Három ágyas szoba', equipment='WiFi, AC, TV, minibar', status=RoomStatus.available),
        ]
        
        for room in rooms_v4:
            db.session.add(room)
            rooms_count += 1
        
        venues.append(venue4)
        
        db.session.commit()
        print(f"✅ {len(venues)} helyszín feltöltve, {rooms_count} szoba hozzáadva")
        return venues


def seed_events(categories, venues):
    """Események feltöltése"""
    with app.app_context():
        print("\n🎫 Események feltöltése...")
        
        events = []
        now = datetime.now()
        
        events_data = [
            {
                'title': 'Python Developer Konferencia 2026',
                'description': 'Az év legnagyobb Python programozási konferenciája',
                'category': categories[1],  # Konferencia
                'venue': venues[0],  # Budapest Kongresszus
                'ticket_price': Decimal('15000'),
                'start': now + timedelta(days=30),
                'end': now + timedelta(days=32),
            },
            {
                'title': 'Rock Fesztivál',
                'description': 'Nyári rockzene fesztivál a legjobbakkal',
                'category': categories[3],  # Fesztivál
                'venue': venues[1],  # Sziget
                'ticket_price': Decimal('25000'),
                'start': now + timedelta(days=60),
                'end': now + timedelta(days=67),
            },
            {
                'title': 'Cristiano Ronaldo - Interklass Futsal',
                'description': 'Szupercsapat futsal mérkőzés',
                'category': categories[2],  # Sportesemény
                'venue': venues[2],  # Papp László
                'ticket_price': Decimal('8000'),
                'start': now + timedelta(days=45),
                'end': now + timedelta(days=45),
            },
            {
                'title': 'Nyíregyháza Opera Gálafellépés',
                'description': 'A világ legjobb énekesei előadása',
                'category': categories[5],  # Театр
                'venue': venues[0],
                'ticket_price': Decimal('12000'),
                'start': now + timedelta(days=25),
                'end': now + timedelta(days=25),
            },
            {
                'title': 'Web Development Workshop',
                'description': 'Gyakorlati webfejlesztési képzés professzionális trénerekkel',
                'category': categories[4],  # Workshop
                'venue': venues[3],  # Debrecen
                'ticket_price': Decimal('18000'),
                'start': now + timedelta(days=20),
                'end': now + timedelta(days=22),
            },
            {
                'title': 'DevOps Masterclass',
                'description': 'Összetett DevOps tanfolyam gyakorlati feladatokkal',
                'category': categories[4],  # Workshop
                'venue': venues[0],
                'ticket_price': Decimal('22000'),
                'start': now + timedelta(days=50),
                'end': now + timedelta(days=52),
            },
            {
                'title': 'Budapest Jazz Night',
                'description': 'Az elmúlt évtizedek legjobbjai előadnak',
                'category': categories[0],  # Koncert
                'venue': venues[2],
                'ticket_price': Decimal('6000'),
                'start': now + timedelta(days=35),
                'end': now + timedelta(days=35),
            },
            {
                'title': 'Közösségi Piac Nap',
                'description': 'Helyi termelők és kézművesek bemutatkozása',
                'category': categories[6],  # Közösségi
                'venue': venues[1],
                'ticket_price': Decimal('0'),  # Ingyenes
                'start': now + timedelta(days=10),
                'end': now + timedelta(days=10),
            },
        ]
        
        for data in events_data:
            event = Event(
                title=data['title'],
                description=data['description'],
                category_id=data['category'].id,
                venue_id=data['venue'].id,
                ticket_price=data['ticket_price'],
            )
            db.session.add(event)
            db.session.flush()
            
            # Adj hozzá eseménytartamokat
            current_time = data['start']
            while current_time <= data['end']:
                event_time = EventTime(
                    event_id=event.id,
                    start_at=current_time,
                    end_at=current_time + timedelta(hours=4)
                )
                db.session.add(event_time)
                current_time += timedelta(days=1)
            
            events.append(event)
        
        db.session.commit()
        print(f"✅ {len(events)} esemény feltöltve")
        return events


def seed_extra_services():
    """Extra szolgáltatások feltöltése"""
    with app.app_context():
        print("\n🎁 Extra szolgáltatások feltöltése...")
        
        services = [
            ExtraService(name='Parkolás', price=Decimal('3000'), description='Alapított parkolóhely'),
            ExtraService(name='Fürdőzselé', price=Decimal('2000'), description='Premium fürdő termékek'),
            ExtraService(name='Reggeli', price=Decimal('4500'), description='Kontinentális reggeli'),
            ExtraService(name='Késői kijelentkezés', price=Decimal('5000'), description='14:00-ig tartozkodás'),
            ExtraService(name='Szobaszervíz', price=Decimal('3000'), description='24/7 szobaszervíz'),
            ExtraService(name='Gyermek ágy', price=Decimal('2500'), description='Kiságy a gyermekeknek'),
            ExtraService(name='Pet tisztálkodás', price=Decimal('5000'), description='Háziállat gondozás'),
        ]
        
        for service in services:
            db.session.add(service)
        
        db.session.commit()
        print(f"✅ {len(services)} extra szolgáltatás feltöltve")
        return services


def seed_bookings(venues, extra_services):
    """Foglalások feltöltése"""
    with app.app_context():
        print("\n🛏️ Foglalások feltöltése...")
        
        users = User.query.filter_by(role=UserRole.guest).all()
        bookings = []
        now = datetime.now()
        
        # Foglalások különböző helyszínekhez
        for i, venue in enumerate(venues):
            rooms = Room.query.filter_by(venue_id=venue.id).limit(2).all()
            
            for j, room in enumerate(rooms):
                check_in = now + timedelta(days=15 + i*10 + j*2)
                check_out = check_in + timedelta(days=2)
                
                booking = Booking(
                    user_id=users[i % len(users)].id,
                    room_id=room.id,
                    check_in=check_in,
                    check_out=check_out,
                    nights=2,
                    total_price=room.price_per_night * 2,
                    status=BookingStatus.confirmed,
                    special_requests=f'Szobaszervíz kérünk a szobához'
                )
                db.session.add(booking)
                db.session.flush()
                
                # Add 1-2 extra szolgáltatást
                for k in range(1, 3):
                    if k < len(extra_services):
                        booking_service = BookingService(
                            booking_id=booking.id,
                            extra_service_id=extra_services[k].id,
                            quantity=1
                        )
                        db.session.add(booking_service)
                
                bookings.append(booking)
        
        db.session.commit()
        print(f"✅ {len(bookings)} foglalás feltöltve")
        return bookings


def seed_reservations(events):
    """Esemény foglalások feltöltése"""
    with app.app_context():
        print("\n📋 Esemény foglalások feltöltése...")
        
        users = User.query.filter_by(role=UserRole.guest).all()
        reservations = []
        
        for i, event in enumerate(events[:4]):  # Csak az első 4 eseményre
            for j in range(1, min(4, len(users) + 1)):
                reservation = Reservation(
                    user_id=users[j % len(users)].id,
                    event_id=event.id,
                    quantity=i % 3 + 1,  # 1-3 jegy
                )
                db.session.add(reservation)
                reservations.append(reservation)
        
        db.session.commit()
        print(f"✅ {len(reservations)} esemény foglalás feltöltve")
        return reservations





def seed_invoices(bookings):
    """Számlák feltöltése"""
    with app.app_context():
        print("\n📄 Számlák feltöltése...")
        
        invoices = []
        now = datetime.now()
        
        for booking in bookings[:5]:  # Csak az első 5 foglaláshoz
            invoice = Invoice(
                booking_id=booking.id,
                invoice_number=f"INV-{now.year}-{booking.id:04d}",
                amount=booking.total_price,
                issued_date=now,
                due_date=now + timedelta(days=30),
                paid_date=now + timedelta(days=5),
                status='paid'
            )
            db.session.add(invoice)
            invoices.append(invoice)
        
        db.session.commit()
        print(f"✅ {len(invoices)} számla feltöltve")
        return invoices


def print_summary():
    """Összefoglalást nyomtat az adatbázisról"""
    with app.app_context():
        print("\n" + "="*60)
        print("📊 ADATBÁZIS FELTÖLTÉSI ÖSSZEFOGLALÁS")
        print("="*60)
        
        print(f"👥 Felhasználók: {User.query.count()}")
        print(f"🏷️ Kategóriák: {Category.query.count()}")
        print(f"🏨 Helyszínek: {Venue.query.count()}")
        print(f"🛏️ Szobák: {Room.query.count()}")
        print(f"🎫 Események: {Event.query.count()}")
        print(f"📝 Eseménytartamok: {EventTime.query.count()}")
        print(f"🛏️ Szobafoglalások: {Booking.query.count()}")
        print(f"🎟️ Esemény foglalások: {Reservation.query.count()}")
        print(f"🎁 Extra szolgáltatások: {ExtraService.query.count()}")
        print(f"📄 Számlák: {Invoice.query.count()}")
        
        print("\n🔐 ADMIN BEJELENTKEZÉS")
        print("="*60)
        print("Email: admin@example.com")
        print("Jelszó: password123")
        print("="*60)
        
        print("\n👤 TEST FELHASZNÁLÓK")
        print("="*60)
        users = User.query.all()
        for user in users:
            print(f"{user.name} ({user.email}) - {user.role.value}")
        
        print("\n🌐 HELYSZÍNEK ÉS SZOBÁK")
        print("="*60)
        venues = Venue.query.all()
        for venue in venues:
            rooms_count = Room.query.filter_by(venue_id=venue.id).count()
            print(f"\n{venue.name} ({venue.city})")
            print(f"  Szobák: {rooms_count}")
            rooms = Room.query.filter_by(venue_id=venue.id).limit(3).all()
            for room in rooms:
                print(f"    - {room.room_number}: {room.capacity} fő, {room.price_per_night} Ft/éj")
        
        print("\n🎫 ESEMÉNYEK")
        print("="*60)
        events = Event.query.all()
        for event in events:
            print(f"• {event.title}")
            print(f"  Helyszín: {event.venue.name}")
            print(f"  Kategória: {event.category.name}")
            print(f"  Jegy ár: {event.ticket_price} Ft")
        
        print("\n✅ Adatbázis feltöltés kész!\n")


def main():
    """Fő függvény"""
    with app.app_context():
        print("🚀 Adatbázis feltöltés kezdődik...\n")
        
        try:
            # Állítsd be a sémát
            ensure_schema()
            
            # Töröld az előző adatokat
            clear_database()
            
            # Tölts fel adatokkal
            users = seed_users()
            categories = seed_categories()
            venues = seed_venues()
            events = seed_events(categories, venues)
            extra_services = seed_extra_services()
            bookings = seed_bookings(venues, extra_services)
            reservations = seed_reservations(events)
            invoices = seed_invoices(bookings)
            
            # Nyomtat összefoglalót
            print_summary()
            
            print("🎉 Adatbázis feltöltés SIKERES!")
            return 0
            
        except Exception as e:
            print(f"\n❌ Hiba az adatbázis feltöltéskor: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == '__main__':
    sys.exit(main())
