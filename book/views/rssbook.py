# -*-coding: utf-8-*-
import base64
import json
import uuid
from io import BytesIO
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import config
from book.utils import get_file_name, get_rss_host
from book.utils.ApiResponse import APIResponse
from book.utils.commUtil import sync_post, return_fun

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/book')


@blueprint.route('/my', methods=['POST'])
@jwt_required()
def my_book():
    """获取我的新闻书籍"""
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/add', methods=['POST'])
@jwt_required()
def book_add():
    """新闻书籍新增"""
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/edit', methods=['POST'])
@jwt_required()
def book_edit():
    """新闻书籍编辑"""
    data = request.get_json()
    if not data['book_id']:
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/del', methods=['POST'])
@jwt_required()
def book_del():
    """新闻书籍删除"""
    data = request.get_json()
    if not data['book_id']:
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/cover', methods=['POST'])
@jwt_required()
def book_cover():
    """新闻书籍封面自定义"""
    coverfile = request.files['coverfile']
    book_id = request.form['book_id']
    user = get_jwt_identity()
    boun = str(uuid.uuid4()).replace("-", "").upper()
    data = MultipartEncoder(
        fields = {'coverfile': (coverfile.name, coverfile, coverfile.mimetype),
                'user_name': user['name'],
                'book_id': book_id,
                'key': config.RSS2EBOOK_KEY
                },
        boundary = f'------{boun}'
    )

    headers = {'Content-Type': data.content_type}
    res = requests.post(url="http://127.0.0.1:8080/api/v2/book/cover", data=data, headers=headers)
    return return_fun(res)
