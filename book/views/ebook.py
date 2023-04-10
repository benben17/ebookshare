# -*-coding: utf-8-*-
import logging

import requests
from flask import request, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

import config
from book.utils import get_file_name, model_to_dict
from book.utils.ApiResponse import APIResponse
from book.models import Userlog, db
blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')


@blueprint.route("/ebook/send", methods=["POST"])
@jwt_required()
def dl_ebook():
    try:
        data = request.get_json()
        book_name = data.get('book_name')
        ipfs_cid = data.get('ipfs_cid')
        if not all(x in data for x in ['book_name', 'ipfs_cid']):
            return APIResponse.internal_server_error(msg="参数错误！")
        user = get_jwt_identity()
        if user.wx_openid is None:
            return APIResponse.bad_request(msg="请先关注公众号，发送注册邮箱进行绑定")
        filesize = data.get('filesize', 0)
        user_log = Userlog(wx_openid=user.wx_openid, book_name=book_name, receive_email=user.kindle_email,
                           user_id=user.id, operation_type='download',
                           status=0, ipfs_cid=ipfs_cid, filesize=filesize)
        db.session.add(user_log)
        db.session.commit()
        return APIResponse.success(msg="发送成功，邮箱接收！")
    except Exception as e:
        logging.error(e)
        return APIResponse.bad_request(msg="发送失败")


@blueprint.route("/ebook/send/log", methods=["POST"])
@jwt_required()
def ebook_send_log():
    user = get_jwt_identity()
    send_logs = Userlog.query.filter_by(user_id=user.id).all()
    if not send_logs:
        return APIResponse.success(msg="无记录")

    data = []
    for log in send_logs:
        data.append(model_to_dict(log))
    APIResponse.success(data=data)


@blueprint.route("/ebook/search", methods=["GET"])
def ebook_search():
    search_url = f'{config.BOOKSEARCH_URL}/search?limit=60&query='
    title = request.args.get("title")
    param = ''
    if title is not None:
        param += f'title:"{title}"'
    res = requests.get(url=search_url + param, timeout=30)
    # print(res.status_code)
    json_res = None
    # print(res.text)
    if int(res.status_code) == 200:
        json_res = res.json()
    return APIResponse.success(data=json_res)