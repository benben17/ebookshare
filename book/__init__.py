# -*-coding: utf-8-*-

from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt_identity
from .dateUtil import utc_to_local
from .logger_config import init_logging
from .schedule import init_scheduler
from .utils import create_app_dir

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app)
jwt = JWTManager(app)

create_app_dir()

with app.app_context():
    from book.models import *

    db.create_all()

from book.views import *

init_logging(app)
#  初始化定时器
init_scheduler(app)

from book.logger_config import *


# @app.after_request
def after_request(response):
    """ Logging all the requests in JSON Per Line Format. """
    audit_logger = logging.getLogger('audit_log')
    try:
        user = get_jwt_identity()
        username = user['name']
    except Exception as e:
        username = ""
    audit_logger.info({
        "datetime": datetime.now(),
        "user_ip": request.remote_addr,
        "user_name": username,
        "method": request.method,
        "request_url": request.path,
        "response_status": response.status,
        "request_referrer": request.referrer,
        "request_user_agent": request.referrer,
        # "request_body": request.json,
        # "response_body": response.json
    })
    return response


@app.errorhandler(404)
def error_date(error):
    return jsonify({'code': 404, 'msg': '404'}), 404


@app.errorhandler(NoAuthorizationError)
@app.errorhandler(InvalidHeaderError)
@app.errorhandler(WrongTokenError)
def handle_auth_error(e):
    return jsonify({'code': 10000, 'msg': 'System error', "data": ""}), 200
