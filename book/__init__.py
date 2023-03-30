# -*-coding: utf-8-*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from datetime import timedelta
from book.wechat import WeChat
import config

app = Flask(__name__)
app.config.from_object('config')

