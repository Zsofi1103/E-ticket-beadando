import os

os.environ["TESTING"] = "true"

from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event
from WebApp.models.reservation import Reservation
from werkzeug.security import generate_password_hash


def run_reservation_test():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        # cleanup
        db.session.query(Reservation).delete()
        db.session.query(Event).delete()
        db.session.query(User).filter(User.email.in_(['user@example.com','admin@example.com'])).delete()
        db.session.commit()

        # create event
        ev = Event(title='Teszt esemény', description='Leiras')
        db.session.add(ev)
        db.session.commit()

        # create regular user
        user = User(name='User', email='user@example.com', password_hash=generate_password_hash('secret'), role='user')
        db.session.add(user)
        # create admin
        admin = User(name='Admin', email='admin@example.com', password_hash=generate_password_hash('admin'), role='admin')
        db.session.add(admin)
        db.session.commit()

        # store ids for later use outside the session
        ev_id = ev.id
        user_id = user.id
        admin_id = admin.id

    with app.test_client() as c:
        # login as user (simulate session)
        with c.session_transaction() as sess:
            sess['user_id'] = user_id

        # reserve
        r = c.post(f'/event/{ev.id}/reserve', follow_redirects=True)
        print('Reserve status:', r.status_code)

        with app.app_context():
            row = db.session.execute(db.select(Reservation).filter_by(event_id=ev_id, user_id=user_id)).first()
            print('Reservation created:', bool(row))
            res_id = row[0].id

        # try duplicate reserve -> should flash error but not create new
        r2 = c.post(f'/event/{ev.id}/reserve', follow_redirects=True)
        print('Duplicate reserve status:', r2.status_code)
        with app.app_context():
            cnt = db.session.query(Reservation).filter_by(event_id=ev_id, user_id=user_id).count()
            print('Reservation count (should be 1):', cnt)

        # logout and login as admin to access admin list and delete
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id

        r3 = c.get('/admin/reservations')
        print('/admin/reservations ->', r3.status_code)

        # admin delete
        r4 = c.post(f'/reservation/delete/{res_id}', follow_redirects=True)
        print('Admin delete status:', r4.status_code)
        with app.app_context():
            cnt2 = db.session.query(Reservation).filter_by(id=res_id).count()
            print('Reservation exists after delete (should be 0):', cnt2)


if __name__ == '__main__':
    run_reservation_test()
