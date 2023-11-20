from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased to accommodate password hash
    audio_records = db.relationship('AudioRecord', backref='author', lazy=True)

    @classmethod
    def create_user(cls, email, password):
        hashed_password = generate_password_hash(password)
        new_user = cls(email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            logging.warning(f"Attempt to register with an already registered email: {email}")
            return 'email_exists'
        except Exception as e:
            db.session.rollback()
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)
            return 'error'

class AudioRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    transcription = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
