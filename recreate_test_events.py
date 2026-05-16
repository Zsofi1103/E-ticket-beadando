from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event
from WebApp.models.reservation import Reservation
from werkzeug.security import generate_password_hash


def run_recreate():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        # ensure we have some users to assign reservations
        users = db.session.query(User).filter(User.email.like('recreate_%')).all()
        if not users:
            for i in range(1, 10):
                u = User(name=f'recU{i}', email=f'recreate_{i}@example.com', password_hash=generate_password_hash('x'), role='user')
                db.session.add(u)
            db.session.commit()
            users = db.session.query(User).filter(User.email.like('recreate_%')).all()
        user_ids = [u.id for u in users]

        # create events E1..E6 if missing
        events = []
        for i in range(1,7):
            title = f'E{i}'
            ev = db.session.scalar(db.select(Event).filter_by(title=title))
            if not ev:
                ev = Event(title=title, description='x')
                db.session.add(ev)
                db.session.commit()
            events.append(ev)

        ids = [e.id for e in events]
        # create reservations counts same as tests
        counts = {0:3,1:5,2:1,3:0,4:2,5:4}
        user_idx = 0
        total_users = len(user_ids)
        created = 0
        for idx, cnt in counts.items():
            for _ in range(cnt):
                uid = user_ids[user_idx % total_users]
                user_idx += 1
                exists = db.session.scalar(db.select(Reservation).filter_by(event_id=ids[idx], user_id=uid))
                if not exists:
                    r = Reservation(event_id=ids[idx], user_id=uid)
                    db.session.add(r)
                    created += 1
        if created:
            db.session.commit()
        print(f'Recreated events E1..E6 and added {created} reservations')


if __name__ == '__main__':
    run_recreate()
