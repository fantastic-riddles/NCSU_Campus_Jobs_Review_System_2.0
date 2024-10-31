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
    db.create_all()

from app import routes, models

if __name__ == "main":
    app.run()