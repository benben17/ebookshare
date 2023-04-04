# encoding:utf-8
import hashlib
import logging
from book import request, cache, app, db, Blueprint
# user = Blueprint('user', __name__)



@app.route('/', methods=['GET', 'POST'])
def home():
    return "欢迎关注 sendtokindles 公众号下载电子书"
