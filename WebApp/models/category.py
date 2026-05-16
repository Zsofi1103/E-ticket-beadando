from WebApp import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    events = db.relationship('Event', secondary='event_categories', back_populates='categories')
