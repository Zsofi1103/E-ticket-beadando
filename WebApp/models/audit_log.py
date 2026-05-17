from WebApp import db
from sqlalchemy import text, ForeignKey


class AuditLog(db.Model):
    """Audit naplózás - összes felhasználói műveletek"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, ForeignKey('booking.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)  # pl: "booking_created", "check_in", "service_added"
    details = db.Column(db.Text, nullable=True)  # JSON formátumban további adatok
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    
    user = db.relationship('User', back_populates='audit_logs')
    booking = db.relationship('Booking', back_populates='audit_logs')
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by user {self.user_id}>"
