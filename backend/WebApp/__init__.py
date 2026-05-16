from flask import Flask
from config import db_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os

# Serve templates and static files from the repository-level `frontend` folder
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
template_dir = os.path.join(repo_root, 'frontend', 'templates')
static_dir = os.path.join(repo_root, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Use an environment variable for secrets. Do NOT commit real secrets to git.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")


config = db_config()

db_port = config.get('port')
db_uri = (
    f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{db_port}/{config['database']}"
)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
log_path = os.path.join(log_dir, 'flask_errors.log')
handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=3)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

from WebApp import models, routes
# NOTE: admin seeding is performed in the Alembic migration file to ensure reproducible
# environments. The startup seeding was removed to avoid duplicate/ambiguous seeds.