# -*-coding: utf-8-*-
# import logging
import logging
from threading import Thread
from flask import request
from flask import Flask
from flask_caching import Cache
from flask_mail import Mail, Message, Attachment
from flask_principal import Principal, identity_loaded, RoleNeed, UserNeed
from flask_login import LoginManager, current_user
from datetime import timedelta
from book.wechat import WeChat
from book.utils import *

logging.basicConfig(filename="book.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)

app = Flask(__name__)
app.config.from_object('config')
principals = Principal(app)
login_manager = LoginManager(app)
# db.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
login_manager.remember_cookie_duration = timedelta(minutes=15)
mail = Mail(app)


# load the extension



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
    logging.info('发送邮件.')
    thr.start()
    return u'发送成功'

cache = Cache(app)


# 定义bookSend()函数


