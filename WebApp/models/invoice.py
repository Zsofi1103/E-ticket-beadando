from WebApp import db
from sqlalchemy import text, ForeignKey


class Invoice(db.Model):
    """Számlák"""
    __tablename__ = 'invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, ForeignKey('booking.id'), nullable=False, unique=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    booking = db.relationship('Booking', back_populates='invoice')
    
    def __repr__(self):
        return f"<Invoice {self.id}: {self.total_amount} Ft ({'fizetve' if self.paid else 'függőben'})>"
