from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from gpt4all import GPT4All
import logging

logging.basicConfig(level=logging.INFO)
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")  # Use the appropriate model identifier

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '8b46acd3fa4cdd9f2d0399310a91e4e9d68776d43ea6e7cf'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import routes
