from WebApp import app, db
from WebApp.models.user import User
from werkzeug.security import generate_password_hash


def create_admin(email: str = 'admin@example.com', password: str = 'admin'):
    with app.app_context():
        existing = db.session.scalar(db.select(User).filter_by(email=email))
        if existing:
            print('Admin already exists:', email)
            return
        admin = User(
            name='Admin',
            email=email,
            password_hash=generate_password_hash(password),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin created:', email)


if __name__ == '__main__':
    create_admin()
from WebApp import app, db
from WebApp.models.user import User
from werkzeug.security import generate_password_hash

ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASS = 'admin'

with app.app_context():
    row = db.session.execute(db.select(User).filter_by(email=ADMIN_EMAIL)).first()
    if row:
        print('Admin already exists:', row[0].email)
    else:
        admin = User(name='Admin', email=ADMIN_EMAIL, password_hash=generate_password_hash(ADMIN_PASS), role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin created:', ADMIN_EMAIL)
