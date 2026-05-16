"""Seed sample events, categories and reservations for development/demo.

This script is safe to run multiple times: it will create missing sample records
and will not duplicate unique-constrained values (email/category name/event title).
"""
from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event
from WebApp.models.category import Category
from WebApp.models.reservation import Reservation
from werkzeug.security import generate_password_hash

SAMPLE_CATEGORIES = [
    ("Zene",),
    ("Színház",),
    ("Kiállítás",),
]

SAMPLE_EVENTS = [
    ("Művészek Éjszakája - Koncert", "Egy felejthetetlen esti koncert helyi és vendégelőadókkal.", ["Zene"]),
    ("Hamlet - Színházi előadás", "Shakespeare klasszikusa kortárs adaptációban.", ["Színház"]),
    ("Kortárs Művészet Kiállítás", "Fiatal művészek csoportos tárlata.", ["Kiállítás"]),
    ("Jazz est a Városligetben", "Kellemes szabadtéri jazzkoncert a parkban.", ["Zene"]),
    ("Operett Est", "Vidám dallamok és tánc egy estére.", ["Színház"]),
]

SAMPLE_USERS = [
    ("demo1@example.com", "Demo One"),
    ("demo2@example.com", "Demo Two"),
    ("demo3@example.com", "Demo Three"),
]


def get_or_create_category(name):
    c = db.session.scalar(db.select(Category).filter_by(name=name))
    if c:
        return c
    c = Category(name=name)
    db.session.add(c)
    db.session.commit()
    return c


def get_or_create_user(email, name):
    u = db.session.scalar(db.select(User).filter_by(email=email))
    if u:
        return u
    u = User(name=name, email=email, password_hash=generate_password_hash('password'), role='user')
    db.session.add(u)
    db.session.commit()
    return u


def get_or_create_event(title, description, category_names):
    e = db.session.scalar(db.select(Event).filter_by(title=title))
    if e:
        return e
    e = Event(title=title, description=description)
    for cname in category_names:
        c = get_or_create_category(cname)
        e.categories.append(c)
    db.session.add(e)
    db.session.commit()
    return e


def run_seed():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        # create categories and events
        events = []
        for title, desc, cats in SAMPLE_EVENTS:
            e = get_or_create_event(title, desc, cats)
            events.append(e)

        # create some demo users
        users = []
        for email, name in SAMPLE_USERS:
            u = get_or_create_user(email, name)
            users.append(u)

        # create some reservations: assign first two users to first two events
        # avoid duplications
        created = 0
        for i, ev in enumerate(events[:4]):
            user = users[i % len(users)]
            exists = db.session.scalar(db.select(Reservation).filter_by(event_id=ev.id, user_id=user.id))
            if not exists:
                r = Reservation(event_id=ev.id, user_id=user.id)
                db.session.add(r)
                created += 1
        if created:
            db.session.commit()
        print(f"Seed finished: events={len(events)}, users={len(users)}, new reservations={created}")


if __name__ == '__main__':
    run_seed()
