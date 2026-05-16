from WebApp import app, db
from WebApp.routes import event_new
import traceback

def run():
    from flask import session
    with app.test_request_context('/event/new'):
        try:
            # set session user to admin if exists
            from WebApp.models.user import User
            admin = db.session.scalar(db.select(User).filter_by(role='admin'))
            if admin:
                session['user_id'] = admin.id
                print('Using admin id', admin.id)
            else:
                print('No admin user found; calling without login')
            resp = event_new()
            print('Rendered event_new successfully:', type(resp))
        except Exception as e:
            print('Exception while rendering event_new:')
            traceback.print_exc()

if __name__ == '__main__':
    run()
