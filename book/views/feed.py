# -*-coding: utf-8-*-

from datetime import datetime, timedelta
import time
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from book.dateUtil import dt_to_str, str_to_dt
from book.dicts import RequestStatus, UserRole
from book.models import User, db
from book.utils import get_file_name, get_rss_host, check_email
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
    if 'timezone' in param:  # 同步更新用户的 timezone
        userinfo = User.get_by_id(user['id'])
        userinfo.timezone = param['timezone']
        db.session.add(userinfo)
        db.session.commit()

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
    from book import cache
    # 获取当前登录用户的身份信息
    user = get_jwt_identity()
    # 获取请求中的参数
    param = request.get_json()
    # 设置缓存的 key 值
    key = f'deliver:{user["name"]}'

    # 如果当前用户没有订阅源，删除缓存并返回错误信息
    if User.get_feed_count(int(user['id'])) == 0:
        cache.delete(key)
        return APIResponse.bad_request(msg='No feed to deliver!')
    # 获取上一次推送的时间
    last_delivery_time = str_to_dt(cache.get(key))
    # 获取当前用户的角色
    user_role = user['role'] if user['role'] else 'default'
    # 获取发送间隔时间，转换成秒
    send_interval = int(UserRole.get_send_interval(user_role)) * 60 * 60
    # 如果上次推送时间存在，并且当前用户不是管理员或测试用户
    if last_delivery_time and user["name"] not in ["admin", "171720928"]:
        # 计算当前时间与上次推送时间的时间差
        elapsed_time = int(time.time()) - int(last_delivery_time.timestamp())
        # 如果时间差小于发送间隔时间，返回错误信息
        if elapsed_time < send_interval:
            remaining_time = send_interval - elapsed_time
            return APIResponse.bad_request(msg=f"{last_delivery_time}已推送，请{remaining_time // 3600}小时后再做推送")

    res = sync_post(request.path, param, user)
    # 如果发送成功，设置缓存的过期时间为发送间隔时间，返回成功信息和结果数据
    if res['status'].lower() == RequestStatus.OK:
        cache.set(key, dt_to_str(datetime.now()), timeout=send_interval)
        return APIResponse.success(msg='Add push task', data=res['data'])
    else:  # 如果发送失败，返回错误信息
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/rss/pub', methods=['POST'])
@jwt_required()
def get_pub_rss():
    """公共订阅源"""
    api_path = '/api/v2/rss/pub'
    res = sync_post(api_path, request.get_json(), get_jwt_identity())
    return return_fun(res)


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
    myuser = get_jwt_identity()
    data = request.get_json()
    if 'custom' in data and data['custom'] and is_rss_feed(data['url']) is False:
        return APIResponse.bad_request(msg='The url is not a correct rss, or cannot be connected')
    res = sync_post(api_path, data, myuser)
    if res['status'].lower() == RequestStatus.OK:
        user = User.get_by_id(myuser['id'])
        feed_num = UserRole.role_feed_num(user.role if user.role else '')
        if user.feed_count >= feed_num:
            return APIResponse.bad_request(msg=f"已达到最大{feed_num}个订阅,不能在订阅")
        user.feed_count += 1
        db.session.add(user)
        db.session.commit()
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/rss/del', methods=['POST'])
@jwt_required()
def my_rss_del():
    """删除我的订阅"""
    api_path = '/api/v2/rss/del'
    res = sync_post(api_path, request.get_json(), get_jwt_identity())
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
    res = sync_post(request.path, request.get_json(), get_jwt_identity())
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
