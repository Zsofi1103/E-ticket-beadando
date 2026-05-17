from flask import Flask
from config import db_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Workaround for Python 3.14 compatibility with Flask/Werkzeug
# This fixes the ast.Str issue in Python 3.14
import ast

class _StrProxy(ast.Constant):
    """Proxy wrapper for ast.Str compatibility in Python 3.14+"""
    def __init__(self, s):
        super().__init__(value=s)
        self.s = s

if not hasattr(ast, 'Str'):
    ast.Str = _StrProxy

# Serve templates and static files from WebApp directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Use an environment variable for secrets. Do NOT commit real secrets to git.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")


try:
    config = db_config()
    db_port = config.get('port')
    db_uri = (
        f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{db_port}/{config['database']}"
    )
except Exception as e:
    # If config.ini is missing or invalid, fall back to SQLite
    app.logger.warning(f"DB config error: {e}. Falling back to SQLite.")
    db_uri = "sqlite:///hotelbooking.db"

# Use SQLite for testing (override)
if os.environ.get("FLASK_ENV") == "testing" or os.environ.get("TESTING") == "true":
    db_uri = "sqlite:///:memory:"

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_path = os.path.join(log_dir, 'flask_errors.log')
handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=3)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

from WebApp import models, routes  # noqa: E402,F401
from WebApp.blueprints import guest_bp  # noqa: E402,F401
from WebApp.blueprints.admin import admin_bp  # noqa: E402,F401

# OpenAPI/Swagger documentation
try:
    from flasgger import Flasgger
    from WebApp.api.swagger_config import swagger_config, api_info
    
    app.config["SWAGGER"] = {
        "title": "Event-Ticket + Hotel Booking API",
        "version": "1.0.0",
        "description": "REST API for Event management and Hotel room booking system"
    }
    
    flasgger = Flasgger(app, config=swagger_config)
except ImportError:
    app.logger.warning("Flasgger not installed - API documentation unavailable")
except Exception as e:
    app.logger.warning(f"Failed to initialize Flasgger: {e}")

# Blueprints regisztrálása
app.register_blueprint(guest_bp)
app.register_blueprint(admin_bp)

# Initialize database schema in testing mode (SQLite :memory:)
if os.environ.get("TESTING") == "true":
    with app.app_context():
        db.create_all()

# NOTE: admin seeding is performed in the Alembic migration file to ensure reproducible
# environments. The startup seeding was removed to avoid duplicate/ambiguous seeds.
