from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import db, PO  # Replace with your actual application and model import

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Adjust based on your database URI
db.init_app(app)

with app.app_context():
    # Drop the table
    PO.__table__.drop(db.engine)

    # Recreate the table
    db.create_all()

