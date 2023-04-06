# -*-coding: utf-8-*-
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, Blueprint, redirect
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail, Message, Attachment
from datetime import timedelta, date
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config.from_object('config')
# principals = Principal(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.session_protection = 'strong'
# login_manager.remember_cookie_duration = timedelta(minutes=15)
mail = Mail(app)
cache = Cache(app)

db = SQLAlchemy(app)
from book.dbModels import *

with app.app_context():
    db.create_all()
# load the extension

from book.views import user, feed, wechat, myfeed


# app.register_blueprint(user, url_prefix='user')
# app.register_blueprint(feed, url_prefix='feed')
# app.register_blueprint(wechat, url_prefix='')


"""
初始化日志
"""
logging.basicConfig(level=logging.INFO)  # 调试debug级(开发环境)
file_log_handler = RotatingFileHandler("{}/logs/books.log".format(os.path.dirname(app.root_path)),
                                       maxBytes=1024 * 1024 * 100, backupCount=10)  # 100M
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s')  # 时间,日志级别,记录日志文件,行数,信息
# 将日志记录器指定日志的格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)



login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
login_manager.remember_cookie_duration = timedelta(minutes=15)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


