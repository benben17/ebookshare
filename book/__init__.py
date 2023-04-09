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



mail = Mail(app)
cache = Cache(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
with app.app_context():
    db.create_all()


def register_extensions(app):
    db.init_app(app)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


@app.errorhandler(NoAuthorizationError)
@app.errorhandler(InvalidHeaderError)
@app.errorhandler(WrongTokenError)
def handle_auth_error(e):
    return jsonify({'code': 10000, 'msg': str(e), "data": ""}), 200


@app.errorhandler(404)
def error_date(error):
    return render_template("404.html"), 404


from book.views import *
modules = ['user', 'ebook', 'feed', 'wechat']
for model_name in modules:
    model = import_module(f"{app.name}.views.{model_name}")
    app.register_blueprint(model.blueprint)




"""
Initialize logging
"""
logfile = f"{os.path.dirname(app.root_path)}/logs/books.log"
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100, backupCount=10)  # 最大100M
# Time, log level, log file, line number, message
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)


