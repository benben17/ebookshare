# -*-coding: utf-8-*-
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse
from book.utils.commUtil import sync_post, return_fun

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')


@blueprint.route('/book/my', methods=['POST'])
@jwt_required()
def my_book():
    """获取我的新闻书籍"""
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/book/add', methods=['POST'])
@jwt_required()
def book_add():
    """新闻书籍新增"""
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/book/edit', methods=['POST'])
@jwt_required()
def book_edit():
    """新闻书籍编辑"""
    data = request.get_json()
    if not data['book_id']:
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/book/del', methods=['POST'])
@jwt_required()
def book_del():
    """新闻书籍删除"""
    data = request.get_json()
    if not data['book_id']:
        return APIResponse.bad_request(msg="参数错误！")
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)
