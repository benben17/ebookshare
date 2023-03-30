# -*-coding: utf-8-*-
from flask import Flask
from flask import request, make_response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_principal import Principal, identity_loaded, RoleNeed, UserNeed
from flask_login import LoginManager, current_user
from datetime import timedelta
from book.wechat import WeChat
from book.utils import *
from book.models import *

app = Flask(__name__)
app.config.from_object('config')
# load the extension
principals = Principal(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
login_manager.remember_cookie_duration = timedelta(minutes=15)

