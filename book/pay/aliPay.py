import json
import logging
import string
import time
from random import random

import requests
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request as flask_request
from book.dicts import Product
from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse
from base64 import b64encode
from urllib.parse import urlparse


blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/alipay')
logger = logging.getLogger()


@blueprint.route("/payment", methods=['GET', 'POST'])
@jwt_required()
def payment():
    data = flask_request.get_json()
    user = get_jwt_identity()
    if str(data.get('product')).lower() not in ("month", "year", 'rss2ebook'):
        return APIResponse.bad_request(msg="Missing required product")

    p_dict = Product(data.get('product')).get_product()
    p_name, p_amount, p_desc = p_dict['name'], p_dict['amount'], p_dict['desc']

