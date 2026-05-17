from WebApp import db
from sqlalchemy import ForeignKey


class BookingService(db.Model):
    """N:N kapcsolat Booking és ExtraService között"""
    __tablename__ = 'booking_service'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, ForeignKey('booking.id'), nullable=False)
    service_id = db.Column(db.Integer, ForeignKey('extra_service.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    booking = db.relationship('Booking', back_populates='services')
    service = db.relationship('ExtraService', back_populates='booking_services')
    
    def __repr__(self):
        return f"<BookingService: {self.service.name} x{self.quantity}>"
