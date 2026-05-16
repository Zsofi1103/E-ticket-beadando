from sqlalchemy import UniqueConstraint, text
from WebApp import db


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)

    __table_args__ = (UniqueConstraint('event_id', 'user_id', name='uq_event_user'),)

    event = db.relationship('Event', back_populates='reservations')
    user = db.relationship('User', back_populates='reservations')
