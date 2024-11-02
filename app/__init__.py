"""
This module initializes and configures the Flask application for a job portal.

The `app` is set up with:
- Configuration loaded from a separate `Config` object.
- SQLAlchemy for database handling.
- Flask-Migrate for handling database migrations.

Key Components:
- `app`: The main Flask application instance, configured with necessary settings.
- `db`: The SQLAlchemy instance for ORM and database interactions.
- `migrate`: The Flask-Migrate instance for database migrations.

Upon the first request, all necessary tables are created if they do not already exist.

Modules Imported:
- `routes`: Handles the routing and view logic.
- `models`: Defines the database models.

The application can be run directly if this module is executed as the main program.
"""

from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "homelander"
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.before_first_request
def create_table():
    """
    Creates tables before the initial requests
    """
    db.create_all()

from app import routes, models

if __name__ == "main":
    app.run()
