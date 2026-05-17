from flask import Blueprint, render_template, redirect, url_for, flash, request
from WebApp import db, app
from WebApp.models.room import Room, RoomStatus
from WebApp.models.venue import Venue
from WebApp.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(fn):
    """Admin jogosultság ellenőrzése"""
    from functools import wraps
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import session
        user_id = session.get('user_id')
        if not user_id:
            flash('Bejelentkezés szükséges', 'hiba')
            return redirect(url_for('login'))
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin():
            flash('Admin jogosultság szükséges', 'hiba')
            return redirect(url_for('index'))
        
        return fn(*args, **kwargs)
    
    return wrapper


@admin_bp.route('/rooms')
@admin_required
def rooms_list():
    """
    List all hotel rooms (Admin only)
    ---
    tags:
      - Administration
    summary: List all rooms
    description: Retrieve paginated list of all hotel rooms with their details
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: Successfully retrieved rooms list
        schema:
          type: object
          properties:
            rooms:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  room_number:
                    type: string
                  capacity:
                    type: integer
                  price_per_night:
                    type: number
                  status:
                    type: string
                    enum: [available, occupied, maintenance, unavailable]
                  venue:
                    type: object
                  created_at:
                    type: string
                    format: datetime
      403:
        description: Admin access required
    """
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    
    per_page = 20
    rooms = db.paginate(
        db.select(Room).order_by(Room.room_number),
        page=page,
        per_page=per_page
    )
    
    return render_template('admin/rooms_list.html', rooms=rooms, page=page)


@admin_bp.route('/rooms/new', methods=['GET', 'POST'])
@admin_required
def room_new():
    """
    Create a new hotel room (Admin only)
    ---
    tags:
      - Administration
    summary: Create new room
    description: Add a new hotel room to the system
    security:
      - Bearer: []
    parameters:
      - name: room_number
        in: formData
        type: string
        required: true
        description: Unique room number identifier
      - name: capacity
        in: formData
        type: integer
        required: true
        description: Number of guests the room can accommodate
      - name: price_per_night
        in: formData
        type: number
        required: true
        description: Price per night in HUF
      - name: venue_id
        in: formData
        type: integer
        description: Optional venue ID to associate room with location
      - name: description
        in: formData
        type: string
        description: Room description
      - name: equipment
        in: formData
        type: string
        description: Equipment/amenities (comma-separated)
      - name: status
        in: formData
        type: string
        enum: [available, occupied, maintenance, unavailable]
        default: available
    responses:
      200:
        description: Room created successfully
      400:
        description: Validation error
      403:
        description: Admin access required
    """
    if request.method == 'POST':
        try:
            room = Room(
                room_number=request.form.get('room_number'),
                capacity=int(request.form.get('capacity', 1)),
                price_per_night=float(request.form.get('price_per_night', 0)),
                description=request.form.get('description'),
                equipment=request.form.get('equipment'),
                status=RoomStatus[request.form.get('status', 'available')],
                venue_id=int(request.form.get('venue_id')) if request.form.get('venue_id') else None
            )
            
            db.session.add(room)
            db.session.commit()
            flash(f'Szoba "{room.room_number}" sikeresen létrehozva', 'sikeres')
            return redirect(url_for('admin.rooms_list'))
        except ValueError as e:
            flash(f'Adatmegadási hiba: {e}', 'hiba')
            db.session.rollback()
        except Exception as e:
            flash(f'Hiba a szoba létrehozásakor: {e}', 'hiba')
            db.session.rollback()
    
    venues = db.session.query(Venue).order_by(Venue.name).all()
    return render_template('admin/room_form.html', room=None, venues=venues, statuses=RoomStatus)


@admin_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@admin_required
def room_edit(room_id):
    """Szoba szerkesztése"""
    room = db.session.get(Room, room_id)
    if not room:
        flash('Nincs ilyen szoba', 'hiba')
        return redirect(url_for('admin.rooms_list'))
    
    if request.method == 'POST':
        try:
            room.room_number = request.form.get('room_number')
            room.capacity = int(request.form.get('capacity', 1))
            room.price_per_night = float(request.form.get('price_per_night', 0))
            room.description = request.form.get('description')
            room.equipment = request.form.get('equipment')
            room.status = RoomStatus[request.form.get('status', 'available')]
            room.venue_id = int(request.form.get('venue_id')) if request.form.get('venue_id') else None
            
            db.session.commit()
            flash(f'Szoba "{room.room_number}" sikeresen frissítve', 'sikeres')
            return redirect(url_for('admin.rooms_list'))
        except ValueError as e:
            flash(f'Adatmegadási hiba: {e}', 'hiba')
            db.session.rollback()
        except Exception as e:
            flash(f'Hiba a szoba szerkesztésekor: {e}', 'hiba')
            db.session.rollback()
    
    venues = db.session.query(Venue).order_by(Venue.name).all()
    return render_template('admin/room_form.html', room=room, venues=venues, statuses=RoomStatus)


@admin_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@admin_required
def room_delete(room_id):
    """Szoba törlése"""
    room = db.session.get(Room, room_id)
    if not room:
        flash('Nincs ilyen szoba', 'hiba')
        return redirect(url_for('admin.rooms_list'))
    
    # Foglalások ellenőrzése
    if room.bookings and len(room.bookings) > 0:
        flash('Ez a szoba nem törölhető, mert van rá foglalás', 'hiba')
        return redirect(url_for('admin.rooms_list'))
    
    try:
        room_number = room.room_number
        db.session.delete(room)
        db.session.commit()
        flash(f'Szoba "{room_number}" sikeresen törölve', 'sikeres')
    except Exception as e:
        flash(f'Hiba a szoba törlésekor: {e}', 'hiba')
        db.session.rollback()
    
    return redirect(url_for('admin.rooms_list'))
