# -*-coding: utf-8-*-

from logging.handlers import RotatingFileHandler
from threading import Thread
from flask import Flask, request, Blueprint
from flask_caching import Cache
from flask_mail import Mail, Message, Attachment
from datetime import timedelta
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

from book.views import user, feed, wechat


# app.register_blueprint(user, url_prefix='user')
# app.register_blueprint(feed, url_prefix='feed')
# app.register_blueprint(wechat, url_prefix='')


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, body, receiver, attach=None):
    msg = Message(subject, recipients=[receiver])
    if attach is not None:
        try:
            with open(attach, 'rb') as f:
                msg.attach(subject, 'application/octet-stream', f.read())
        except Exception as e:
            logging.error('open file failed.' + e)

    msg.html = body
    thr = Thread(target=send_async_email, args=[app, msg])
    logging.info(f'发送邮件.{subject}-接收邮箱{receiver}')
    thr.start()
    return u'发送成功'


"""
初始化日志
"""
logging.basicConfig(level=logging.INFO)  # 调试debug级(开发环境)
file_log_handler = RotatingFileHandler("{}/logs/books.log".format(app.root_path.replace("/book", "")),
                                       maxBytes=1024 * 1024 * 100, backupCount=10)  # 100M
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(filename)s:%(lineno)d %(message)s')  # 时间,日志级别,记录日志文件,行数,信息
# 将日志记录器指定日志的格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)
