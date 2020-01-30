from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .database import db, migration
from .routes import bp
from .config import BaseConfig


def register_extensions(app):
    db.init_app(app)
    # migration.init(app, db)
# db = SQLAlchemy(app)
# migration = Migrate(app, db)


def start_api_server():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    register_extensions(app)
    import backend.models
    app.register_blueprint(bp, api_prefix='/api')
    app.run(debug=True, host='0.0.0.0')