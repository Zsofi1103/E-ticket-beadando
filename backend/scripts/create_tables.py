"""One-off helper: create missing tables in the configured database.

Usage (PowerShell):

    python scripts/create_tables.py

This runs `db.create_all()` inside the Flask app context. It's intended for
development convenience to create newly added SQLAlchemy models (like
`EventTime`) when you don't want to run Alembic migrations right now.

Note: For production use you should create and run Alembic/Flask-Migrate
migrations instead of using create_all().
"""
import sys
from WebApp import app, db


def main():
    print('Starting create_all() to ensure tables exist...')
    try:
        with app.app_context():
            db.create_all()
        print('create_all() finished successfully.')
    except Exception as e:
        print('create_all() failed:', e)
        sys.exit(2)


if __name__ == '__main__':
    main()
