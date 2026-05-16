from sqlalchemy import text
from WebApp import db
from WebApp.models.event import favorites


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)

    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Event', secondary=favorites, back_populates='favorited_by')

    def is_admin(self):
        return self.role == 'admin'
