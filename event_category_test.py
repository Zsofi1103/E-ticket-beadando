from WebApp import app, db
from WebApp.models.user import User
from WebApp.models.event import Event
from WebApp.models.category import Category
from WebApp.models.reservation import Reservation
from werkzeug.security import generate_password_hash


def run_event_category_tests():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        db.session.query(Reservation).delete()
        db.session.query(Event).delete()
        db.session.query(Category).delete()
        db.session.query(User).filter(User.email.in_(['user2@example.com','admin2@example.com'])).delete()
        db.session.commit()

        user = User(name='User2', email='user2@example.com', password_hash=generate_password_hash('secret'), role='user')
        admin = User(name='Admin2', email='admin2@example.com', password_hash=generate_password_hash('admin'), role='admin')
        db.session.add_all([user, admin])
        db.session.commit()

        user_id = user.id
        admin_id = admin.id

        ev = Event(title='Base Event', description='base')
        db.session.add(ev)
        db.session.commit()
        ev_id = ev.id

    with app.test_client() as c:
        # 1) Non-admin cannot create event via route
        with c.session_transaction() as sess:
            sess['user_id'] = user_id
        with app.app_context():
            before_count = db.session.query(Event).count()
        r = c.post('/event/new', data={'title': 'UserCreated', 'description': 'x'}, follow_redirects=True)
        with app.app_context():
            after_count = db.session.query(Event).count()
        print('Non-admin create prevented:', before_count == after_count)

        # 2) Admin can create event
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post('/event/new', data={'title': 'AdminCreated', 'description': 'x'}, follow_redirects=True)
        with app.app_context():
            created = db.session.execute(db.select(Event).filter_by(title='AdminCreated')).first()
        print('Admin create succeeded:', bool(created))
        if created:
            created_id = created[0].id
        else:
            created_id = None

        # 3) Non-admin cannot edit existing event
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = user_id
        r = c.post(f'/event/edit/{ev_id}', data={'title': 'Hacked Title', 'description': 'y'}, follow_redirects=True)
        with app.app_context():
            evr = db.session.get(Event, ev_id)
            print('Non-admin edit prevented:', evr.title == 'Base Event')

        # 4) Admin can edit
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post(f'/event/edit/{ev_id}', data={'title': 'Updated By Admin', 'description': 'new'}, follow_redirects=True)
        with app.app_context():
            evr = db.session.get(Event, ev_id)
            print('Admin edit succeeded:', evr.title == 'Updated By Admin')

        # 5) Attach reservation and category to event, ensure admin deletion is blocked
        with app.app_context():
            # attach category
            cat = Category(name='CatForEvent')
            db.session.add(cat)
            db.session.commit()
            cat_id = cat.id
            ev_obj = db.session.get(Event, ev_id)
            ev_obj.categories.append(cat)
            # add reservation by user
            res = Reservation(event_id=ev_id, user_id=user_id)
            db.session.add(res)
            db.session.commit()
        # admin attempts delete
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post(f'/event/delete/{ev_id}', follow_redirects=True)
        with app.app_context():
            still_exists = db.session.get(Event, ev_id) is not None
            print('Event deletion blocked when refs exist (should be True):', still_exists)

        # 6) Category deletion blocked while referenced
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post(f'/category/delete/{cat_id}', follow_redirects=True)
        with app.app_context():
            cat_exists = db.session.get(Category, cat_id) is not None
            print('Category deletion blocked when referenced (should be True):', cat_exists)

        # cleanup: remove reservation and detach category, then admin delete should succeed
        with app.app_context():
            db.session.query(Reservation).filter_by(event_id=ev_id).delete()
            ev_obj = db.session.get(Event, ev_id)
            ev_obj.categories = []
            db.session.commit()
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post(f'/event/delete/{ev_id}', follow_redirects=True)
        with app.app_context():
            gone = db.session.get(Event, ev_id) is None
            print('Event deletion after cleanup succeeded:', gone)
        with c.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = admin_id
        r = c.post(f'/category/delete/{cat_id}', follow_redirects=True)
        with app.app_context():
            cat_gone = db.session.get(Category, cat_id) is None
            print('Category deletion after cleanup succeeded:', cat_gone)


if __name__ == '__main__':
    run_event_category_tests()
