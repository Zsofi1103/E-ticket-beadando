import os

os.environ["TESTING"] = "true"

from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event
from WebApp.models.reservation import Reservation
from WebApp.managers.eventmanager import EventManager
from werkzeug.security import generate_password_hash
import uuid


def run_top_events_test():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        # cleanup
        db.session.query(Reservation).delete()
        db.session.query(Event).delete()
        db.session.query(User).filter(User.email.in_(['t1@example.com','t2@example.com','t3@example.com'])).delete()
        db.session.commit()

        # create a pool of users to allow multiple reservations per event
        users = []
        for i in range(1, 15):
            unique_email = f'u{i}_{uuid.uuid4().hex[:8]}@example.com'
            u = User(name=f'U{i}', email=unique_email, password_hash=generate_password_hash('x'), role='user')
            db.session.add(u)
            users.append(u)
        db.session.commit()
        user_ids = [u.id for u in users]

        # create events
        evs = []
        for i in range(1,7):
            e = Event(title=f'E{i}', description='x')
            db.session.add(e)
            evs.append(e)
        db.session.commit()
        ids = [e.id for e in evs]

        # create reservations: E1:3, E2:5, E3:1, E4:0, E5:2, E6:4
        counts = {0:3,1:5,2:1,3:0,4:2,5:4}
        # create reservations using distinct users so unique constraint isn't violated
        user_idx = 0
        total_users = len(user_ids)
        for idx, cnt in counts.items():
            for _ in range(cnt):
                uid = user_ids[user_idx % total_users]
                user_idx += 1
                r = Reservation(event_id=ids[idx], user_id=uid)
                db.session.add(r)
        db.session.commit()

        em = EventManager(db)
        top = em.top_events(limit=5)
        print('Top events length:', len(top))
        # Expect order by counts desc: E2(5), E6(4), E1(3), E5(2), E3(1)
        titles = [row[0].title for row in top]
        print('Top titles:', titles)
        expected = ['E2','E6','E1','E5','E3']
        print('Order correct:', titles == expected)

if __name__ == '__main__':
    run_top_events_test()
