from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize the database and migration tools
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app
