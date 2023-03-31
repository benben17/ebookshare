# -*-coding: utf-8-*-
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
                fileType = get_file_suffix(attach)
                msg.attach(subject+"."+fileType, 'application/octet-stream', f.read())
        except Exception as e:
            logging.error('open file failed.' + e)

    msg.html = body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return u'发送成功'

cache = Cache(app)
