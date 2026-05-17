from WebApp import db
from sqlalchemy import text


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(500), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)

    events = db.relationship('Event', back_populates='venue')
    rooms = db.relationship('Room', back_populates='venue', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name!r}>"
