# -*-coding: utf-8-*-

from datetime import datetime, timedelta
import time
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from book.dateUtil import dt_to_str, str_to_dt
from book.dicts import RequestStatus, UserRole
from book.models import User, db
from book.utils import get_file_name, get_rss_host
from book.utils.ApiResponse import APIResponse
from book.utils.commUtil import return_fun, sync_post
from book.utils.rssUtil import get_rss_latest_titles, is_rss_feed

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')


@blueprint.route('/sync/user/add', methods=['POST'])
@jwt_required()
def user_add():
    """用户同步"""
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/sync/user/seting', methods=['POST'])
@jwt_required()
def user_setting():
    """用户设置"""
    param = request.get_json()
    user = get_jwt_identity()
    res = sync_post(request.path, param, user)
    return return_fun(res)


@blueprint.route('/sync/user/upgrade', methods=['POST'])
@jwt_required()
def user_upgrade():
    """订阅用户升级到付费用户"""
    param = request.get_json()
    user = get_jwt_identity()
    res = sync_post(request.path, param, user)
    return return_fun(res)


@blueprint.route('/sync/user/info', methods=['POST'])
@jwt_required()
def rss_user_info():
    param = request.get_json()
    user = get_jwt_identity()
    res = sync_post(request.path, param, user)
    return return_fun(res)


@blueprint.route('/deliver/logs', methods=['POST'])
@jwt_required()
def get_deliver_logs():
    """获取发送订阅日志"""
    param = request.get_json()
    user = get_jwt_identity()
    res = sync_post(request.path, param, user)
    return return_fun(res)


@blueprint.route('/deliver/push', methods=['POST'])
@jwt_required()
def my_feed_deliver():
    DELIVER_TIMEOUT = 23 * 60 * 60
    from book import cache
    user = get_jwt_identity()
    key = f'deliver:{user["name"]}'
    last_delivery_time = str_to_dt(cache.get(key))

    if last_delivery_time and user["name"] not in ["admin", "171720928"]:
        elapsed_time = time.time() - last_delivery_time.timestamp()
        if elapsed_time < DELIVER_TIMEOUT:
            remaining_time = DELIVER_TIMEOUT - elapsed_time
            return APIResponse.bad_request(msg=f"{last_delivery_time}已推送，请{remaining_time // 3600}小时后再做推送")

    cache.set(key, dt_to_str(datetime.now()), timeout=DELIVER_TIMEOUT)
    return return_fun(sync_post(request.path, request.get_json(), get_jwt_identity()))


@blueprint.route('/my/rss', methods=['POST'])
@jwt_required()
def my_rss():
    api_path = '/api/v2/rss/myrss'
    res = sync_post(api_path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/my/rss/add', methods=['POST'])
@jwt_required()
def my_rss_add():
    api_path = '/api/v2/rss/add'
    res = sync_post(api_path, request.get_json(), get_jwt_identity())
    if res['status'].lower() == 'ok':
        myuser = get_jwt_identity()
        user = User.query.get(myuser['id'])
        feed_num = UserRole.role_feed_num(user.role)
        if user.feed_count >= feed_num:
            return APIResponse.bad_request(msg=f"已达到最大{feed_num}个订阅,不能在订阅")
        user.feed_count += 1
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
    res = sync_post(api_path, request.get_json(), get_jwt_identity())
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
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/rss/invalid', methods=['POST'])
@jwt_required()
def rss_invalid():
    res = sync_post(request.path,request.get_json(), get_jwt_identity())
    return return_fun(res)


@blueprint.route('/rss/view/title', methods=['POST'])
@jwt_required()
def rss_view_title():
    data = request.get_json()
    if not data.get('url'):
        return APIResponse.bad_request(msg='params error')
    if is_rss_feed(data.get('url')) is False:
        return APIResponse.bad_request(msg='rss invalid,please declare invalid rss')

    article = get_rss_latest_titles(data.get('url'), data.get('num', 10))
    return APIResponse.success(data=article)


if __name__ == "__main__":
    from book.utils.rssUtil import rss_list
    from book import app, cache

    timeout = 23 * 60 * 60
    print(datetime.now() + timedelta(seconds=timeout))
