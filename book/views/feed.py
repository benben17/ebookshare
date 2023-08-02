# -*-coding: utf-8-*-

import logging
from datetime import datetime, timedelta
import time
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from book.dateUtil import dt_to_str, str_to_dt
from book.dicts import RequestStatus, UserRole
from book.models import User, db
from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse
from book.utils.commUtil import return_fun, sync_post, cacheKey
from book.utils.rssUtil import get_rss_latest_titles, is_rss_feed
from book import cache as cacheUtil

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
    if 'timezone' in user and not user['timezone']:
        if 'timezone' in param:  # 同步更新用户的 timezone
            userinfo = User.get_by_id(user['id'])
            userinfo.timezone = param['timezone']
            db.session.add(userinfo)
            db.session.commit()

    res = sync_post(request.path, param, user)
    if res.get("status").lower() == RequestStatus.OK:
        user_info_key = cacheKey.get_key('rss_user_info',user['name'])
        cacheUtil.set(user_info_key, res.get("data"), timeout=86400)
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
    user_info_cache = cacheUtil.get(cacheKey.get_key('rss_user_info',user['name']))

    if user_info_cache:
        return APIResponse.success(data=user_info_cache)
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
    # 获取当前登录用户的身份信息
    user = get_jwt_identity()
    # 获取请求中的参数
    param = request.get_json()
    deliver_key = cacheKey.get_key('deliver_key', user['name'])
    # 获取上一次推送的时间
    last_delivery_time = str_to_dt(cacheUtil.get(deliver_key))
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
        cacheUtil.set(deliver_key, dt_to_str(datetime.now()), timeout=send_interval)
        return APIResponse.success(msg='Add push task', data=res['data'])
    else:  # 如果发送失败，返回错误信息
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/rss/pub', methods=['POST'])
def get_pub_rss():
    """公共订阅源"""
    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
        if user:
            cache_pub_rss_key = cacheKey.get_key('pub_rss_key', user['name'])
            pub_rss = cacheUtil.get(cache_pub_rss_key)
            if pub_rss:
                return APIResponse.success(data=pub_rss)
            res = sync_post(request.path, request.get_json(), user)
            if res.get("status").lower() == RequestStatus.OK:
                cacheUtil.set(cache_pub_rss_key, res.get('data'), timeout=86400)
            return return_fun(res)
    except Exception as e:
        logging.error(f"获取失败：{e.args}")
        if cacheUtil.get(cacheKey.get_key('pub_rss_key')):
            return APIResponse.success(data=cacheUtil.get(cacheKey.get_key('pub_rss_key')))
        res = sync_post(path=request.path, param=request.get_json(), user=None)
        if res['status'] == RequestStatus.OK:
            cacheUtil.set(cacheKey.get_key('pub_rss_key'), res['data'], timeout=86400)
        return return_fun(res)


@blueprint.route('/my/rss', methods=['POST'])
@jwt_required()
def my_rss():
    api_path = '/api/v2/rss/myrss'
    user = get_jwt_identity()
    cache_key = cacheKey('my_rss',user['name'])
    my_rss_cache = cacheUtil.getcache_key()
    if my_rss_cache:
        return APIResponse.success(data=my_rss_cache)

    res = sync_post(api_path, request.get_json(), user)
    if res.get("status").lower() == RequestStatus.OK:
        cacheUtil.set(cache_key, res.get("data"), timeout=86400)

    return return_fun(res)


@blueprint.route('/my/rss/add', methods=['POST'])
@jwt_required()
def my_rss_add():
    api_path = '/api/v2/rss/add'
    user_info = get_jwt_identity()
    data = request.get_json()
    if 'custom' in data and data['custom'] and is_rss_feed(data['url']) is False:
        return APIResponse.bad_request(msg='The url is not a correct rss, or cannot be connected')

    user = User.get_by_id(user_info['id'])
    feed_num = UserRole.role_feed_num(user.role)
    if user.feed_count >= feed_num:
        return APIResponse.bad_request(msg=f"已达到最大 {feed_num} 个订阅,不能在订阅,请升级成Plus会员！")
    res = sync_post(api_path, data, user_info)
    if res['status'].lower() == RequestStatus.OK:
        user.feed_count += 1
        db.session.add(user)
        db.session.commit()
        cacheUtil.delete(cacheKey.get_key('pub_rss_key',user.name))
        cacheUtil.delete(cacheKey.get_key('my_rss',user.name))
        cacheUtil.delete(cacheKey.get_key('mybook',user.name))
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/rss/del', methods=['POST'])
@jwt_required()
def my_rss_del():
    """删除我的订阅"""
    api_path = '/api/v2/rss/del'
    user_info = get_jwt_identity()
    res = sync_post(api_path, request.get_json(), user_info)

    if res['status'].lower() == RequestStatus.OK:
        user = User.query.get(user_info['id'])
        user.feed_count = user.feed_count - 1 if user.feed_count == 0 else 0
        db.session.add(user)
        db.session.commit()

        cacheUtil.delete(cacheKey.get_key('pub_rss_key',user_info['name']))
        cacheUtil.delete(cacheKey.get_key('my_rss',user_info['name']))
        cacheUtil.delete(cacheKey.get_key('mybook',user_info['name']))
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

    a = "//aaa"
    print("http:".join(a))
    print(cacheKey.get_key('pub_rss_key',"a"))
    print(''.lower())
    # timeout = 24 * 60 * 60
    # print(timeout)
    # print(datetime.now() + timedelta(seconds=timeout))
