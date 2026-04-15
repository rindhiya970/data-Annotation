"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    return app
