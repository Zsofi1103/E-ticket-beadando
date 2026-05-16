from WebApp import app, db
from WebApp.models.user import User
import traceback

def run():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        admin = db.session.scalar(db.select(User).filter_by(role='admin'))
        if not admin:
            print('No admin user found')
            return
        with app.test_client() as client:
            # set session user_id
            with client.session_transaction() as sess:
                sess['user_id'] = admin.id
            # pick a category id
            from WebApp.models.category import Category
            cat = db.session.query(Category).first()
            data = {
                'title': 'TEST EVENT FROM SCRIPT',
                'description': 'Description created by test script',
                'category_id': str(cat.id) if cat else ''
            }
            try:
                resp = client.post('/event/new', data=data, follow_redirects=True)
                print('Status code:', resp.status_code)
                print(resp.get_data(as_text=True)[:2000])
            except Exception:
                print('Exception during POST:')
                traceback.print_exc()

if __name__ == '__main__':
    run()
