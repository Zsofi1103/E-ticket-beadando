from WebApp import app, db
from WebApp.managers.eventmanager import EventManager

def run():
    from WebApp.models.event import Event
    em = EventManager(db)
    with app.app_context():
        # list a few events and print categories
        rows = db.session.query(Event).order_by(Event.created_at.desc()).limit(10).all()
        for r in rows:
            cats = [c.name for c in r.categories]
            print(f'ID={r.id} TITLE={r.title!r} CATEGORIES={cats}')

if __name__ == '__main__':
    run()
