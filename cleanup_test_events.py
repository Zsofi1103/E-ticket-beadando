"""Cleanup script: remove test events like E1..E9 with description 'x'.
Run this from project root: `python cleanup_test_events.py`
"""
from WebApp import app, db
from WebApp.models.event import Event
from WebApp.models.reservation import Reservation


def run_cleanup():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()

        q = db.session.query(Event).filter((Event.description == 'x') | (Event.title.like('E%')))
        events = q.all()
        if not events:
            print('No matching test events found.')
            return
        ids = [e.id for e in events]

        res_deleted = db.session.query(Reservation).filter(Reservation.event_id.in_(ids)).delete(synchronize_session=False)

        ev_deleted = 0
        for e in events:
            db.session.delete(e)
            ev_deleted += 1
        db.session.commit()
        print(f'Deleted events: {ev_deleted}, reservations removed: {res_deleted}')


if __name__ == '__main__':
    run_cleanup()
