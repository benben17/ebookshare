# -*-coding: utf-8-*-
import json
import requests
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import config
from book.models import User, db
from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse

headers = {'Content-Type': 'application/x-www-form-urlencoded'}
blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')


@blueprint.route('/sync/user/add', methods=['POST'])
def user_add():
    """用户同步"""
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/sync/user/seting', methods=['POST'])
@jwt_required()
def user_setting():
    """用户设置"""
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/sync/user/upgrade', methods=['POST'])
@jwt_required()
def user_upgrade():
    """订阅用户升级到付费用户"""
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/sync/user/info', methods=['POST'])
@jwt_required()
def rss_user_info():
    res = sync_post(request.path)
    if res['status'] == "ok":
        user_info = res['data']
        return APIResponse.success(data=user_info)
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
    res = sync_post(request.path)
    if res['status'] == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/rss', methods=['POST'])
@jwt_required()
def my_rss():
    api_path = '/api/v2/rss/myrss'
    res = sync_post(api_path)
    if res['status'].lower() == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/rss/add', methods=['POST'])
@jwt_required()
def my_rss_add():
    api_path = '/api/v2/rss/add'
    res = sync_post(api_path)
    if res['status'].lower() == 'ok':
        myuser = get_jwt_identity()
        user = User.query.get(myuser['id'])
        if user.feed_count >= 5 and user.role == config.DEFAULT_USER_ROLE:
            return APIResponse.bad_request(msg="已达到最大订阅数，请升级用户")
        if user.feed_count >= 100:
            return APIResponse.bad_request(msg="已达到最大订阅数")
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
    if res['status'] == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/my/rss/del', methods=['POST'])
@jwt_required()
def my_rss_del():
    """删除我的订阅"""
    api_path = '/api/v2/rss/del'
    res = sync_post(api_path)
    user = get_jwt_identity()
    if res['status'].lower() == 'ok':
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
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@blueprint.route('/rss/invalid', methods=['POST'])
@jwt_required()
def rss_invalid():
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


def sync_post(path):
    data = request.get_json()
    user = get_jwt_identity()
    if data:
        data['key'] = config.RSS2EBOOK_KEY
        data['user_name'] = user['name']
        data['creator'] = user['name']
    rss_host = config.rss_host['primary']
    res = requests.post(rss_host + path, data=data, headers=headers, timeout=60)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        if json_data['status'] == "ok":
            return json_data
        return {"status": "failed", "msg": json_data['msg']}
    else:
        return {"status": "failed", "msg": res.text}



if __name__ == "__main__":
        rss_list = [('Science / Latest Science News', 'https://www.sciencedaily.com/rss/top.xml', 'false', 'tech'),
                ('Science / All Top News', 'https://www.sciencedaily.com/rss/top/science.xml', 'false', 'tech'),
                ('Science / Health News', 'https://www.sciencedaily.com/rss/top/health.xml', 'false', 'tech'),
                ('Science / Technology News', 'https://www.sciencedaily.com/rss/top/technology.xml', 'false', 'tech'),
                ('Science / Environment News', 'https://www.sciencedaily.com/rss/top/environment.xml', 'false', 'tech'),
                ('Science / Society News', 'https://www.sciencedaily.com/rss/top/society.xml', 'false', 'tech'),
                (
                'Science / Strange &amp; Offbeat News', 'https://www.sciencedaily.com/rss/strange_offbeat.xml', 'false',
                'tech')]
        for rss in rss_list:
            path = '/api/v2/rss/share'
            data = {'key': config.RSS2EBOOK_KEY,
                    'user_name': 'admin',
                    'creator': 'admin',
                    "title": rss[0],
                    "url": rss[1],
                    "is_fulltext": rss[2],
                    "category": rss[3]
                    }
            request_url = config.rss_host['primary']
            # request_url = "http://127.0.0.1:8080"
            res = requests.post(request_url + path, data=data, headers=headers, timeout=60)
            print(rss)
            print(res.text,res.status_code)