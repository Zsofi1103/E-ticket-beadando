import json
from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event, event_categories
from WebApp.models.category import Category
from WebApp.models.reservation import Reservation


def row_to_dict(obj, include=None):
    d = {}
    for c in obj.__table__.columns:
        name = c.name
        val = getattr(obj, name)

        try:
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
        except Exception:
            pass
        d[name] = val
    if include:
        for key in include:
            d[key] = getattr(obj, key)
    return d


def run_export():
    with app.app_context():
        out = {}
        users = db.session.query(User).all()
        out['users'] = [row_to_dict(u) for u in users]
        events = db.session.query(Event).all()
        out['events'] = [row_to_dict(e) for e in events]
        categories = db.session.query(Category).all()
        out['categories'] = [row_to_dict(c) for c in categories]

        ec_rows = []
        try:
            res = db.session.execute(event_categories.select()).all()
            for r in res:
                ec_rows.append(dict(r._mapping))
        except Exception:
            ec_rows = []
        out['event_categories'] = ec_rows
        reservations = db.session.query(Reservation).all()
        out['reservations'] = [row_to_dict(r) for r in reservations]
        with open('eticket_dump_before_restore.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print('Exported DB to eticket_dump_before_restore.json')


if __name__ == '__main__':
    run_export()
