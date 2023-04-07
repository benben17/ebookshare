# -*-coding: utf-8-*-
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, jsonify
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
with app.app_context():
    db.create_all()

"""
Initialize logging
"""
logging.basicConfig(level=logging.INFO)  # Debug level (development environment)
file_log_handler = RotatingFileHandler(
    f"{os.path.dirname(app.root_path)}/logs/books.log", maxBytes=1024 * 1024 * 100, backupCount=10
)  # 100M
formatter = logging.Formatter(
    '%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s'
)  # Time, log level, log file, line number, message
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)

jwt = JWTManager(app)

@app.errorhandler(NoAuthorizationError)
@app.errorhandler(InvalidHeaderError)
@app.errorhandler(WrongTokenError)
def handle_auth_error(e):
    return jsonify({'code': 10000, 'msg': str(e), "data": ""}), 200

@app.errorhandler(404)
def error_date(error):
    return render_template("404.html"), 404

# Register blueprints
# app.register_blueprint(user, url_prefix='/user')
# app.register_blueprint(feed, url_prefix='/feed')
# app.register_blueprint(wechat, url_prefix='/')
# app.register_blueprint(myfeed, url_prefix='/myfeed')


from book.dbModels import *
