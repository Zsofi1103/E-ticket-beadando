from WebApp import app, db
from WebApp.models.user import User


def run_profile_test():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    test_email = 'profiletest@example.com'
    test_password = 'oldpass123'
    new_password = 'newpass456'

    with app.app_context():
        db.create_all()
        # cleanup previous
        prev = db.session.execute(db.select(User).filter_by(email=test_email)).first()
        if prev:
            db.session.delete(prev[0])
            db.session.commit()

    with app.test_client() as client:
        # register
        r = client.post('/register', data={
            'name': 'Profile Test',
            'email': test_email,
            'password': test_password,
            'password2': test_password,
        }, follow_redirects=True)
        print('Register status:', r.status_code)

        # login
        r = client.post('/login', data={'email': test_email, 'password': test_password}, follow_redirects=True)
        print('Login status:', r.status_code)

        # GET edit page
        r = client.get('/profile/edit')
        print('GET /profile/edit ->', r.status_code)

        # POST update name and change password
        r = client.post('/profile/edit', data={
            'name': 'Profile Renamed',
            'current_password': test_password,
            'new_password': new_password,
            'new_password2': new_password,
        }, follow_redirects=True)
        print('POST /profile/edit ->', r.status_code)

        # check profile shows new name
        r = client.get('/profile')
        body = r.get_data(as_text=True)
        print('Profile contains new name:', 'Profile Renamed' in body)

        # logout and login with new password
        client.get('/logout')
        r = client.post('/login', data={'email': test_email, 'password': new_password}, follow_redirects=True)
        print('Login with new password status:', r.status_code)


if __name__ == '__main__':
    run_profile_test()
