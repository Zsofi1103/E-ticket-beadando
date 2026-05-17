"""
Guest Routes Blueprint - Szobakeresés és foglalás funkciók
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from WebApp import db
from WebApp.models import Room, Booking, BookingStatus, ExtraService, Invoice, AuditLog, User
from datetime import datetime, timedelta
from decimal import Decimal
import json

guest_bp = Blueprint('guest', __name__, url_prefix='/guest')


def get_current_user():
    """Aktuális felhasználó lekérése"""
    uid = session.get('user_id')
    if not uid:
        return None
    try:
        return db.session.get(User, uid)
    except Exception:
        return None


def log_audit(user_id, action, booking_id=None, details=None):
    """Audit log bejegyzés rögzítése"""
    try:
        audit = AuditLog(
            user_id=user_id,
            booking_id=booking_id,
            action=action,
            details=details
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {e}")


@guest_bp.route('/search', methods=['GET', 'POST'])
def search_rooms():
    """
    Search for available rooms
    ---
    tags:
      - Bookings
    summary: Search available hotel rooms
    description: Find available rooms based on check-in/check-out dates and guest count
    parameters:
      - name: check_in
        in: formData
        type: string
        format: date
        required: true
        description: Check-in date (YYYY-MM-DD)
      - name: check_out
        in: formData
        type: string
        format: date
        required: true
        description: Check-out date (YYYY-MM-DD)
      - name: guests_count
        in: formData
        type: integer
        required: true
        description: Number of guests
    responses:
      200:
        description: Search results with available rooms
      400:
        description: Invalid search parameters
    """
    available_rooms = []
    search_data = None
    
    if request.method == 'POST':
        try:
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            guests_count = int(request.form.get('guests_count', 1))
            
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
            
            if check_in >= check_out:
                flash('A bejelentkezési dátum előbb kell legyen, mint a kijelentkezési!', 'error')
                return redirect(url_for('guest.search_rooms'))
            
            if check_out > datetime.now() + timedelta(days=365):
                flash('Maximum 1 év előre lehet foglalni!', 'error')
                return redirect(url_for('guest.search_rooms'))
            
            search_data = {
                'check_in': check_in,
                'check_out': check_out,
                'guests_count': guests_count
            }
            
            # Összes szoba lekérése
            all_rooms = Room.query.filter_by(status='available').all()
            
            # Szobák szűrése kapacitás és elérhetőség alapján
            for room in all_rooms:
                if room.capacity >= guests_count and room.is_available(check_in, check_out):
                    nights = (check_out - check_in).days
                    price = float(room.price_per_night) * nights
                    available_rooms.append({
                        'room': room,
                        'price': price,
                        'nights': nights
                    })
            
        except Exception as e:
            flash(f'Keresési hiba: {str(e)}', 'error')
    
    return render_template('guest/search_rooms.html', 
                         available_rooms=available_rooms, 
                         search_data=search_data,
                         now=datetime.now())


@guest_bp.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    """Szoba foglalása"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        try:
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            guests_count = int(request.form.get('guests_count', 1))
            
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
            
            # Validáció
            if guests_count > room.capacity:
                flash(f'Maximum {room.capacity} vendég lehet!', 'error')
                return redirect(url_for('guest.book_room', room_id=room_id))
            
            if not room.is_available(check_in, check_out):
                flash('A szoba nem elérhető az adott időszakban!', 'error')
                return redirect(url_for('guest.search_rooms'))
            
            # Foglalás létrehozása
            nights = (check_out - check_in).days
            total_price = float(room.price_per_night) * nights
            
            booking = Booking(
                user_id=user.id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                guests_count=guests_count,
                total_price=Decimal(str(total_price)),
                status=BookingStatus.pending
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Invoice létrehozása
            invoice = Invoice(
                booking_id=booking.id,
                total_amount=Decimal(str(total_price))
            )
            db.session.add(invoice)
            
            # Audit log
            log_audit(user.id, 'booking_created', booking.id, 
                     f'Foglalás: {room.room_number}, {nights} éj, {total_price} Ft')
            
            db.session.commit()
            
            flash(f'Foglalás sikeresen létrehozva! (ID: {booking.id})', 'success')
            return redirect(url_for('guest.booking_detail', booking_id=booking.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hiba a foglalás során: {str(e)}', 'error')
    
    return render_template('guest/book_room.html', room=room)


@guest_bp.route('/bookings', methods=['GET'])
def my_bookings():
    """Saját foglalások listája"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    
    return render_template('guest/my_bookings.html', bookings=bookings)


@guest_bp.route('/booking/<int:booking_id>', methods=['GET'])
def booking_detail(booking_id):
    """Foglalás részletei"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Jogosultság ellenőrzése
    if booking.user_id != user.id and not user.is_admin():
        flash('Nincs jogosultsága!', 'error')
        return redirect(url_for('guest.my_bookings'))
    
    services = booking.services
    
    return render_template('guest/booking_detail.html', booking=booking, services=services)


@guest_bp.route('/booking/<int:booking_id>/edit', methods=['GET', 'POST'])
def edit_booking(booking_id):
    """Foglalás módosítása"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user.id:
        flash('Nincs jogosultsága!', 'error')
        return redirect(url_for('guest.my_bookings'))
    
    if not booking.can_be_modified():
        flash('A foglalást nem lehet módosítani ebben az állapotban!', 'error')
        return redirect(url_for('guest.booking_detail', booking_id=booking_id))
    
    if request.method == 'POST':
        try:
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            guests_count = int(request.form.get('guests_count', booking.guests_count))
            
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
            
            if guests_count > booking.room.capacity:
                flash(f'Maximum {booking.room.capacity} vendég lehet!', 'error')
                return redirect(url_for('guest.edit_booking', booking_id=booking_id))
            
            # Elérhetőség ellenőrzése (az aktuális foglalást kizárva)
            conflicts = Booking.query.filter(
                Booking.room_id == booking.room_id,
                Booking.id != booking.id,
                Booking.status != BookingStatus.cancelled,
                Booking.check_in < check_out,
                Booking.check_out > check_in
            ).first()
            
            if conflicts:
                flash('A szoba nem elérhető az adott időszakban!', 'error')
                return redirect(url_for('guest.edit_booking', booking_id=booking_id))
            
            # Ár újraszámítása
            nights = (check_out - check_in).days
            old_price = booking.total_price
            new_room_price = float(booking.room.price_per_night) * nights
            services_price = sum(float(s.service.price) * s.quantity for s in booking.services)
            new_total = Decimal(str(new_room_price + services_price))
            
            # Módosítás
            booking.check_in = check_in
            booking.check_out = check_out
            booking.guests_count = guests_count
            booking.total_price = new_total
            
            # Invoice frissítése
            if booking.invoice:
                booking.invoice.total_amount = new_total
            
            # Audit log
            log_audit(user.id, 'booking_modified', booking.id,
                     f'Ár módosítva: {old_price} -> {new_total} Ft')
            
            db.session.commit()
            
            flash('Foglalás sikeresen módosítva!', 'success')
            return redirect(url_for('guest.booking_detail', booking_id=booking_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hiba a módosítás során: {str(e)}', 'error')
    
    return render_template('guest/edit_booking.html', booking=booking)


@guest_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Foglalás lemondása"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user.id:
        flash('Nincs jogosultsága!', 'error')
        return redirect(url_for('guest.my_bookings'))
    
    if not booking.can_be_cancelled():
        flash('A foglalást nem lehet lemondani ebben az állapotban!', 'error')
        return redirect(url_for('guest.booking_detail', booking_id=booking_id))
    
    try:
        booking.status = BookingStatus.cancelled
        log_audit(user.id, 'booking_cancelled', booking.id, 'Felhasználó által lemondva')
        db.session.commit()
        
        flash('Foglalás lemondva!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hiba a lemondás során: {str(e)}', 'error')
    
    return redirect(url_for('guest.my_bookings'))


@guest_bp.route('/booking/<int:booking_id>/invoice')
def download_invoice(booking_id):
    """Számla letöltése (PDF)"""
    user = get_current_user()
    if not user:
        flash('Bejelentkezés szükséges!', 'error')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user.id and not user.is_admin():
        flash('Nincs jogosultsága!', 'error')
        return redirect(url_for('guest.my_bookings'))
    
    # TODO: PDF generálás
    return render_template('guest/invoice.html', booking=booking, now=datetime.now())


@guest_bp.route('/booking/<int:booking_id>/add-service', methods=['POST'])
def add_service(booking_id):
    """Extra szolgáltatás hozzáadása"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not booking.can_be_modified():
        return jsonify({'error': 'Booking cannot be modified'}), 400
    
    try:
        data = request.get_json()
        service_id = data.get('service_id')
        quantity = int(data.get('quantity', 1))
        
        service = ExtraService.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Ellenőrzés: már létezik-e ilyen szolgáltatás
        from WebApp.models.booking_service import BookingService
        existing = BookingService.query.filter_by(
            booking_id=booking.id,
            service_id=service.id
        ).first()
        
        if existing:
            existing.quantity += quantity
        else:
            booking_service = BookingService(
                booking_id=booking.id,
                service_id=service.id,
                quantity=quantity
            )
            db.session.add(booking_service)
        
        # Ár frissítése
        booking.total_price = Decimal(str(booking.calculate_total_price()))
        if booking.invoice:
            booking.invoice.total_amount = booking.total_price
        
        log_audit(user.id, 'service_added', booking.id,
                 f'{service.name} hozzáadva ({quantity}x)')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'service_name': service.name,
            'price': float(service.price),
            'quantity': quantity,
            'total_price': float(booking.total_price)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
