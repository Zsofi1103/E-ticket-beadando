from WebApp import db
from sqlalchemy import text, Enum, ForeignKey
import enum
from datetime import datetime


class BookingStatus(enum.Enum):
    """Foglalás státusza"""
    pending = "pending"
    confirmed = "confirmed"
    checked_in = "checked_in"
    checked_out = "checked_out"
    cancelled = "cancelled"


class Booking(db.Model):
    """Szobafoglalások modellje"""
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    guests_count = db.Column(db.Integer, nullable=False)
    status = db.Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    check_in_time = db.Column(db.DateTime, nullable=True)  # tényleges check-in idő
    check_out_time = db.Column(db.DateTime, nullable=True)  # tényleges check-out idő
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), 
                          onupdate=text("UTC_TIMESTAMP()"), nullable=False)
    
    user = db.relationship('User', back_populates='bookings')
    room = db.relationship('Room', back_populates='bookings')
    services = db.relationship('BookingService', back_populates='booking', cascade='all, delete-orphan')
    invoice = db.relationship('Invoice', back_populates='booking', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='booking', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Booking {self.id}: {self.user.name} - {self.room.room_number} ({self.status.value})>"
    
    def calculate_nights(self):
        """Éjszakák száma"""
        return (self.check_out - self.check_in).days
    
    def calculate_total_price(self):
        """Teljes ár kalkuláció (szoba + extra szolgáltatások)"""
        nights = self.calculate_nights()
        if nights <= 0:
            return 0
        
        room_price = float(self.room.price_per_night) * nights
        services_price = sum(float(s.service.price) * s.quantity for s in self.services)
        
        return room_price + services_price
    
    def can_be_modified(self):
        """Lehet-e módosítani a foglalást?"""
        return self.status in [BookingStatus.pending, BookingStatus.confirmed]
    
    def can_be_cancelled(self):
        """Lehet-e lemondani a foglalást?"""
        return self.status in [BookingStatus.pending, BookingStatus.confirmed]
