# -*-coding: utf-8-*-
import json
import logging

import requests
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import config
from book.dicts import RequestStatus, UserRole
from book.models import User, db
from book.utils import get_file_name, get_rss_host
from book.utils.ApiResponse import APIResponse

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')


def sync_post(path):
    param = request.get_json()
    user = get_jwt_identity()
    if param:
        param['key'] = config.RSS2EBOOK_KEY
        param['user_name'] = user['name']
        param['creator'] = user['name']
    res = requests.post(get_rss_host() + path, data=param, headers=config.HEADERS, timeout=60)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        if json_data['status'] == RequestStatus.OK:
            if RequestStatus.DATA not in json_data.keys():
                json_data['data'] = ""
            return json_data
        return {"status": "failed", "msg": json_data[RequestStatus.MSG]}
    else:
        logging.error(str(path), res.text)
        return {"status": "failed", "msg": res.text}


def return_fun(res):
    if res['status'].lower() == RequestStatus.OK:
        return APIResponse.success(msg=res[RequestStatus.MSG], data=res[RequestStatus.DATA])
    else:
        return APIResponse.bad_request(msg=res[RequestStatus.MSG])


@blueprint.route('/sync/user/add', methods=['POST'])
@jwt_required()
def user_add():
    """用户同步"""
    res = sync_post(request.path)
    return return_fun(res)


@blueprint.route('/sync/user/seting', methods=['POST'])
@jwt_required()
def user_setting():
    """用户设置"""
    res = sync_post(request.path)
    return return_fun()


@blueprint.route('/sync/user/upgrade', methods=['POST'])
@jwt_required()
def user_upgrade():
    """订阅用户升级到付费用户"""
    return return_fun(sync_post(request.path))


@blueprint.route('/sync/user/info', methods=['POST'])
@jwt_required()
def rss_user_info():
    res = sync_post(request.path)
    if res['status'] == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/deliver/logs', methods=['POST'])
@jwt_required()
def get_deliver_logs():
    """获取发送订阅日志"""
    res = sync_post(request.path)
    if res['status'] == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/feed/book/deliver', methods=['POST'])
@jwt_required()
def get_my_feed_deliver():
    return return_fun(sync_post(request.path))


@blueprint.route('/my/rss', methods=['POST'])
@jwt_required()
def my_rss():
    api_path = '/api/v2/rss/myrss'
    res = sync_post(api_path)
    return return_fun(res)


@blueprint.route('/my/rss/add', methods=['POST'])
@jwt_required()
def my_rss_add():
    api_path = '/api/v2/rss/add'
    res = sync_post(api_path)
    if res['status'].lower() == 'ok':
        myuser = get_jwt_identity()
        user = User.query.get(myuser['id'])
        feed_num = UserRole.role_feed_num(user.role)
        if user.feed_count >= 5 and user.role == UserRole.role_name():  # 默认为default
            return APIResponse.bad_request(msg=f"已达到最大{feed_num}个订阅数，请升级用户")
        if user.feed_count >= 100:
            return APIResponse.bad_request(msg=f"已达到最大{feed_num}个订阅,不能在订阅")
        user.feed_count = user.feed_count + 1
        db.session.add(user)
        db.session.commit()
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/rss/pub', methods=['POST'])
@jwt_required()
def get_pub_rss():
    """公共订阅源"""
    api_path = '/api/v2/rss/pub'
    res = sync_post(api_path)
    return return_fun(res)


@blueprint.route('/my/rss/del', methods=['POST'])
@jwt_required()
def my_rss_del():
    """删除我的订阅"""
    api_path = '/api/v2/rss/del'
    res = sync_post(api_path)
    user = get_jwt_identity()
    if res['status'].lower() == RequestStatus.OK:
        user = User.query.get(user['id'])
        user.feed_count = user.feed_count - 1 if user.feed_count == 0 else 0
        db.session.add(user)
        db.session.commit()
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/rss/share', methods=['POST'])
@jwt_required()
def rss_share():
    """订阅源共享"""
    res = sync_post(request.path)
    return return_fun(res)


@blueprint.route('/rss/invalid', methods=['POST'])
@jwt_required()
def rss_invalid():
    res = sync_post(request.path)
    return return_fun(res)


if __name__ == "__main__":
    from book.rss import rss_list

    for rss in rss_list:
        path = '/api/v2/rss/manager'
        data = {'key': config.RSS2EBOOK_KEY,
                'user_name': 'admin',
                'creator': 'admin',
                "title": rss[1],
                "url": rss[2],
                "is_fulltext": "flase",
                "category": rss[0],
                "librss_id": 1
                }
        print(data)
        # request_url = "http://127.0.0.1:8080"
        res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS, timeout=60)
        # print(rss)
        print(res.text, res.status_code)
