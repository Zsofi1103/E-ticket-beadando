from WebApp import db
from sqlalchemy import text, Enum, ForeignKey
import enum


class RoomStatus(enum.Enum):
    """Szoba státusza"""
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"
    unavailable = "unavailable"


class Room(db.Model):
    """Szobák modellje"""
    __tablename__ = 'room'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, ForeignKey('venue.id'), nullable=True)
    room_number = db.Column(db.String(50), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)  # max vendég száma
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    equipment = db.Column(db.String(500), nullable=True)  # vesszővel elválasztott felszereltség
    status = db.Column(Enum(RoomStatus), default=RoomStatus.available, nullable=False)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), 
                          onupdate=text("UTC_TIMESTAMP()"), nullable=False)
    
    venue = db.relationship('Venue', back_populates='rooms')
    bookings = db.relationship('Booking', back_populates='room', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Room {self.room_number}: {self.capacity} ágyas, {self.price_per_night} Ft/éj>"
    
    def is_available(self, check_in, check_out):
        """Ellenőrzi, hogy a szoba szabad-e az adott időszakban"""
        from WebApp.models.booking import Booking, BookingStatus
        
        conflicts = Booking.query.filter(
            Booking.room_id == self.id,
            Booking.status != BookingStatus.cancelled,
            Booking.check_in < check_out,
            Booking.check_out > check_in
        ).first()
        
        return conflicts is None
