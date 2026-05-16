from flask import Flask
from config import db_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os

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

# Initialize database schema in testing mode (SQLite :memory:)
if os.environ.get("TESTING") == "true":
    with app.app_context():
        db.create_all()

# NOTE: admin seeding is performed in the Alembic migration file to ensure reproducible
# environments. The startup seeding was removed to avoid duplicate/ambiguous seeds.
