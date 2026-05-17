from WebApp import db
from sqlalchemy import text


class ExtraService(db.Model):
    """Extra szolgáltatások (párnák, fürdőköpeny, masszázs, stb.)"""
    __tablename__ = 'extra_service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    
    booking_services = db.relationship('BookingService', back_populates='service', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ExtraService {self.name}: {self.price} Ft>"
