# -*-coding: utf-8-*-

import uuid
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import config
from book import cache
from book.dicts import RequestStatus
from book.utils import get_file_name, get_rss_host
from book.utils.ApiResponse import APIResponse
from book.utils.commUtil import sync_post, return_fun, cacheKey

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/book')


@blueprint.route('/my', methods=['POST'])
@jwt_required()
def my_book():
    """获取我的新闻书籍"""
    user = get_jwt_identity()
    my_bk_key = cacheKey.get_key('mybook',user['name'])
    my_books = cache.get(my_bk_key)
    if my_books:
        return APIResponse.success(data=my_books)
    res = sync_post(request.path, request.get_json(), user)
    if res.get("status").lower() == RequestStatus.OK:
        if res.get('data'):
            cache.set(my_bk_key, res.get('data'))
    return return_fun(res)


@blueprint.route('/add', methods=['POST'])
@jwt_required()
def book_add():
    """新闻书籍新增"""
    user = get_jwt_identity()
    res = sync_post(request.path, request.get_json(), user)
    cache.delete(cacheKey.get_key('mybook',user['name']))
    return return_fun(res)


@blueprint.route('/edit', methods=['POST'])
@jwt_required()
def book_edit():
    """新闻书籍编辑"""
    data = request.get_json()
    user = get_jwt_identity()
    if not data.get('book_id'):
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), user)
    cache.delete(cacheKey.get_key('mybook',user['name']))
    return return_fun(res)


@blueprint.route('/del', methods=['POST'])
@jwt_required()
def book_del():
    """新闻书籍删除"""
    data = request.get_json()
    user = get_jwt_identity()
    if not data['book_id']:
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), user)
    cache.delete(cacheKey.get_key('mybook',user['name']))
    return return_fun(res)


@blueprint.route('/builtin', methods=['POST'])
@jwt_required()
def book_builtin_list():
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/cover', methods=['POST'])
@jwt_required()
def book_cover():
    """新闻书籍封面自定义"""
    coverfile = request.files['coverfile']
    book_id = request.form['book_id']
    user = get_jwt_identity()
    bound_str = str(uuid.uuid4()).replace("-", "").upper()
    data = MultipartEncoder(
        fields={'coverfile': (coverfile.name, coverfile, coverfile.mimetype),
                'user_name': user['name'],
                'book_id': book_id,
                'key': config.RSS2EBOOK_KEY},
        boundary=f'------{bound_str}'
    )
    headers = {'Content-Type': data.content_type}
    res = requests.post(url=get_rss_host(), data=data, headers=headers)
    return return_fun(res)
