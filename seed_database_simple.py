#!/usr/bin/env python3
"""
Egyszerűs adatbázis feltöltés szép, reális adatokkal.
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text

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


def main():
    with app.app_context():
        print("🚀 Adatbázis feltöltés kezdődik...\n")
        
        # Törlés és újraalkotás
        print("🗑️ Adatbázis törlése...")
        db.drop_all()
        db.create_all()
        print("✅ Adatbázis visszaállítva\n")
        
        # Felhasználók
        print("👥 Felhasználók feltöltése...")
        users_data = [
            ('Admin Felhasználó', 'admin@example.com', UserRole.admin),
            ('Szálloda Vezetője', 'manager@hotel.com', UserRole.manager),
            ('Recepcióista', 'receptionist@hotel.com', UserRole.receptionist),
            ('John Doe', 'john@example.com', UserRole.guest),
            ('Jane Smith', 'jane@example.com', UserRole.guest),
            ('Kovács Péter', 'peter@example.com', UserRole.guest),
        ]
        users = []
        for name, email, role in users_data:
            user = User(name=name, email=email, role=role)
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        db.session.commit()
        print(f"✅ {len(users)} felhasználó feltöltve\n")
        
        # Kategóriák
        print("🏷️ Kategóriák feltöltése...")
        cat_names = ['Koncert', 'Konferencia', 'Sportesemény', 'Fesztivál', 'Workshop', 'Szabadtéri Előadás', 'Közösségi Esemény']
        categories = []
        for name in cat_names:
            cat = Category(name=name)
            db.session.add(cat)
            categories.append(cat)
        db.session.commit()
        print(f"✅ {len(categories)} kategória feltöltve\n")
        
        # Helyszínek & Szobák
        print("🏨 Helyszínek és szobák feltöltése...")
        venues_data = [
            ('Budapest Kongresszusi Központ', 'Jagelló út 1-3, 1146 Budapest', 5000),
            ('Óbudai-sziget Fesztivál', 'Sziget, Budapest', 100000),
            ('Papp László Sportaréna', 'Stefánia út 2, 1146 Budapest', 12500),
            ('Debrecen Nagycsarnok', 'Baltazár tér 10, 4026 Debrecen', 8000),
        ]
        venues = []
        rooms_count = 0
        for name, addr, cap in venues_data:
            venue = Venue(name=name, address=addr, capacity=cap)
            db.session.add(venue)
            db.session.flush()
            venues.append(venue)
            
            # Szobák - egyes számok a helyszínhez kötve
            rooms_per_venue = [
                (f'{name[0]}01', 2, 15000, 'Két ágyas szoba', 'WiFi, AC, TV, minibar'),
                (f'{name[0]}02', 2, 15000, 'Két ágyas szoba', 'WiFi, AC, TV, minibar'),
                (f'{name[0]}03', 4, 25000, 'Családi szoba', 'WiFi, AC, TV, minibar, konyha'),
            ]
            for room_num, capacity, price, desc, equip in rooms_per_venue:
                room = Room(venue_id=venue.id, room_number=room_num, capacity=capacity, 
                           price_per_night=Decimal(price), description=desc, equipment=equip, 
                           status=RoomStatus.available)
                db.session.add(room)
                rooms_count += 1
        
        db.session.commit()
        print(f"✅ {len(venues)} helyszín, {rooms_count} szoba feltöltve\n")
        
        # Események
        print("🎫 Események feltöltése...")
        now = datetime.now()
        events_data = [
            ('Python Developer Konferencia 2026', 'Az év legnagyobb Python konferenciája', 1, 0, 15000, 30, 32),
            ('Rock Fesztivál', 'Nyári rockzene fesztivál', 3, 1, 25000, 60, 67),
            ('Futsal Mérkőzés', 'Szupercsapat futsal mérkőzés', 2, 2, 8000, 45, 45),
            ('Opera Gálafellépés', 'A világ legjobb énekesei', 5, 0, 12000, 25, 25),
            ('Web Development Workshop', 'Gyakorlati webfejlesztési képzés', 4, 3, 18000, 20, 22),
            ('DevOps Masterclass', 'DevOps tanfolyam', 4, 0, 22000, 50, 52),
            ('Budapest Jazz Night', 'Jazzkonzert', 0, 2, 6000, 35, 35),
            ('Közösségi Piac', 'Helyi termelők bemutatkozása', 6, 1, 0, 10, 10),
        ]
        events = []
        for title, desc, cat_idx, venue_idx, price, start_day, end_day in events_data:
            event = Event(title=title, description=desc, venue_id=venues[venue_idx].id, price=Decimal(price))
            event.categories.append(categories[cat_idx])
            db.session.add(event)
            db.session.flush()
            
            # EventTime-ok
            start = now + timedelta(days=start_day)
            end = now + timedelta(days=end_day)
            current = start
            while current <= end:
                et = EventTime(event_id=event.id, 
                              year=current.year, month=current.month, day=current.day,
                              hour=18, minute=30)
                db.session.add(et)
                current += timedelta(days=1)
            
            events.append(event)
        
        db.session.commit()
        print(f"✅ {len(events)} esemény feltöltve\n")
        
        # Extra szolgáltatások
        print("🎁 Extra szolgáltatások feltöltése...")
        services_data = [
            ('Parkolás', 3000),
            ('Reggeli', 4500),
            ('Késői kijelentkezés', 5000),
            ('Szobaszervíz', 3000),
            ('Gyermek ágy', 2500),
        ]
        services = []
        for name, price in services_data:
            svc = ExtraService(name=name, price=Decimal(price))
            db.session.add(svc)
            services.append(svc)
        db.session.commit()
        print(f"✅ {len(services)} szolgáltatás feltöltve\n")
        
        # Foglalások
        print("🛏️ Foglalások feltöltése...")
        rooms = db.session.query(Room).all()
        bookings = []
        for i, room in enumerate(rooms[:8]):
            check_in = now + timedelta(days=15 + i*2)
            check_out = check_in + timedelta(days=2)
            booking = Booking(user_id=users[(i+1) % len(users)].id, room_id=room.id,
                             check_in=check_in, check_out=check_out, guests_count=2,
                             total_price=room.price_per_night * 2, status=BookingStatus.confirmed)
            db.session.add(booking)
            db.session.flush()
            
            # Adj extra szolgáltatásokat
            for j in range(1, min(3, len(services)+1)):
                bs = BookingService(booking_id=booking.id, service_id=services[j].id, quantity=1)
                db.session.add(bs)
            
            bookings.append(booking)
        
        db.session.commit()
        print(f"✅ {len(bookings)} foglalás feltöltve\n")
        
        # Esemény foglalások
        print("📋 Esemény foglalások feltöltése...")
        reservations = []
        for i, event in enumerate(events[:4]):
            for j in range(1, 4):
                res = Reservation(user_id=users[j].id, event_id=event.id)
                db.session.add(res)
                reservations.append(res)
        
        db.session.commit()
        print(f"✅ {len(reservations)} esemény foglalás feltöltve\n")
        
        # Számlák
        print("📄 Számlák feltöltése...")
        invoices = []
        for booking in bookings[:5]:
            inv = Invoice(booking_id=booking.id, total_amount=booking.total_price, paid=True, 
                         paid_at=now+timedelta(days=5))
            db.session.add(inv)
            invoices.append(inv)
        
        db.session.commit()
        print(f"✅ {len(invoices)} számla feltöltve\n")
        
        # Összefoglalás
        print("=" * 60)
        print("📊 ADATBÁZIS FELTÖLTÉSI ÖSSZEFOGLALÁS")
        print("=" * 60)
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
        print("=" * 60)
        print("Email: admin@example.com")
        print("Jelszó: password123")
        print("=" * 60)
        
        print("\n✅ Adatbázis feltöltés SIKERES!")
        print("\nIndítsd el az alkalmazást:")
        print("  python app.py")
        print("\nJelentkezz be az admin@example.com fiókkal!")


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Hiba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
