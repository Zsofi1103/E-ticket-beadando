from sqlalchemy import text
from WebApp import db

event_categories = db.Table(
    'event_categories',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
)

favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    start_at = db.Column(db.DateTime, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)

    categories = db.relationship('Category', secondary=event_categories, back_populates='events')
    reservations = db.relationship('Reservation', back_populates='event', cascade='all, delete-orphan')
    times = db.relationship('EventTime', back_populates='event', cascade='all, delete-orphan')
    favorited_by = db.relationship('User', secondary=favorites, back_populates='favorites')
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=True)
    venue = db.relationship('Venue', back_populates='events')