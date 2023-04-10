# -*-coding: utf-8-*-
import os
import logging
from importlib import import_module
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_caching import Cache
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app)
jwt = JWTManager(app)

from book.models import *
with app.app_context():
    db_dir = os.path.join(app.root_path, "db")
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    db.create_all()

log_dir = os.path.join(app.root_path, "log")
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
ebooks_dir = os.path.join(app.root_path, "ebooks")
if not os.path.exists(ebooks_dir):
    os.mkdir(ebooks_dir)

@app.errorhandler(NoAuthorizationError)
@app.errorhandler(InvalidHeaderError)
@app.errorhandler(WrongTokenError)
def handle_auth_error(e):
    return jsonify({'code': 10000, 'msg': str(e), "data": ""}), 200


from book.views import *

modules = ['user', 'ebook', 'feed', 'wechat']
for model_name in modules:
    model = import_module(f"{app.name}.views.{model_name}")
    app.register_blueprint(model.blueprint)

"""
Initialize logging
"""
logfile = f"{os.path.dirname(app.root_path)}/logs/books.log"
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100, backupCount=10)  # 最大100M
# Time, log level, log file, line number, message
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

from .models import *
