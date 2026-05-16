from WebApp import app, db
from WebApp.models.event import Event
from WebApp.models.category import Category


def run_assign():
    with app.app_context():
        db.create_all()
        default_name = 'Egyéb'
        c = db.session.scalar(db.select(Category).filter_by(name=default_name))
        if not c:
            c = Category(name=default_name)
            db.session.add(c)
            db.session.commit()
        assigned = 0
        events = db.session.query(Event).all()
        for e in events:
            if not getattr(e, 'categories', None) or len(e.categories) == 0:
                e.categories.append(c)
                assigned += 1
        if assigned:
            db.session.commit()
        print(f'Assigned default category "{default_name}" to {assigned} events')


if __name__ == '__main__':
    run_assign()
