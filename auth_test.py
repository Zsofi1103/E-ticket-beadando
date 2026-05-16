import os

os.environ["TESTING"] = "true"

from WebApp import app, db
from WebApp.models.user import User


def run_auth_test():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    test_email = 'testuser@example.com'
    test_password = 'testpass'

    with app.app_context():

        db.create_all()

        prev = db.session.execute(db.select(User).filter_by(email=test_email)).first()
        if prev:
            u = prev[0]
            db.session.delete(u)
            db.session.commit()

    with app.test_client() as client:
    
        resp = client.post('/register', data={
            'name': 'Test User',
            'email': test_email,
            'password': test_password,
            'password2': test_password,
        }, follow_redirects=True)
        print('Register status:', resp.status_code)

        with app.app_context():
            row = db.session.execute(db.select(User).filter_by(email=test_email)).first()
            print('User created:', bool(row))


        resp = client.post('/login', data={
            'email': test_email,
            'password': test_password,
        }, follow_redirects=True)
        print('Login status:', resp.status_code)

        resp = client.get('/profile')
        print('Profile status:', resp.status_code)
        print(resp.get_data(as_text=True)[:1000])


if __name__ == '__main__':
    run_auth_test()
from WebApp import app, db

def run():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

    with app.test_client() as c:
        print('GET /register')
        r = c.get('/register')
        print(r.status_code)
        data = {'name':'Test User','email':'test@example.com','password':'secret123','password2':'secret123'}
        r = c.post('/register', data=data, follow_redirects=True)
        print('POST /register ->', r.status_code)
        print('Registration response contains success message:', 'Sikeres regisztráció' in r.get_data(as_text=True))
        r = c.get('/logout', follow_redirects=True)
        data = {'email':'test@example.com','password':'secret123'}
        r = c.post('/login', data=data, follow_redirects=True)
        print('POST /login ->', r.status_code)
        r = c.get('/profile')
        print('GET /profile ->', r.status_code)
        print(r.get_data(as_text=True)[:800])

if __name__ == '__main__':
    run()
