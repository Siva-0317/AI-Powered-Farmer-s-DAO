# backend/database.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    db_path = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__), 'db.sqlite3')}")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app
