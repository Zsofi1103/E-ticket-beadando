#!/usr/bin/env python
"""Initialize database tables on live MySQL"""
import sys
sys.path.insert(0, '.')

from app import app
from WebApp import db

print(f'Database URI: {app.config["SQLALCHEMY_DATABASE_URI"][:60]}...')

with app.app_context():
    print('Creating all tables...')
    db.create_all()
    print('Tables created successfully!')
