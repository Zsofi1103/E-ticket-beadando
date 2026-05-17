from sqlalchemy import text, Enum
from WebApp import db
from WebApp.models.event import favorites
import enum
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    """Felhasználói szerepkörök"""
    guest = "guest"
    receptionist = "receptionist"
    manager = "manager"
    admin = "admin"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.guest)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)

    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Event', secondary=favorites, back_populates='favorited_by')
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')

    def is_admin(self):
        return self.role == UserRole.admin
    
    def is_receptionist(self):
        return self.role in [UserRole.receptionist, UserRole.manager, UserRole.admin]
    
    def is_manager(self):
        return self.role in [UserRole.manager, UserRole.admin]
    
    def is_guest(self):
        return self.role == UserRole.guest
    
    def set_password(self, password):
        """Jelszó beállítása hash formátumban"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Jelszó ellenőrzése"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.email}: {self.name} ({self.role.value})>"
