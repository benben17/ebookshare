import json
import logging

import requests
from flask_jwt_extended import jwt_required

import config
from book import app, request, Blueprint, User, db
from flask import jsonify

from book.ApiResponse import APIResponse

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

rss2ebook_key = 'rss2Ebook.com.luck!'
# 用户同步
@app.route('/api/v2/sync/user/add',  methods=['POST'])
@jwt_required()
def user_add():
    return sync_post(request.path)

# 用户设置
@app.route('/api/v2/sync/user/seting',  methods=['POST'])
@jwt_required()
def user_setting():
    return jsonify(request.path)

@app.route('/api/v2/sync/user/upgrade',  methods=['POST'])
@jwt_required()
def user_upgrade():
    return sync_post(request.path)

# 获取发送日志
@app.route('/api/v2/my/deliver/logs',methods=['POST'])
@jwt_required()
def get_deliver_logs():
    return sync_post(request.path)

@app.route('/api/v2/feed/book/deliver',methods=['POST'])
@jwt_required()
def get_my_feed_deliver():
    return sync_post(request.path)

@app.route('/api/v2/my/rss/add',methods=['POST'])
@jwt_required()
def get_my_rss_add():
    data = request.get_json()
    api_path = '/api/v2/rss/add'
    res = sync_post(api_path)
    if res['data']['status'] == 'ok':
        user = User.query.filter(User.name == data['user_name']).get()
        user.feed_count = user.feed_count+1
        db.session.add(user)
        db.session.commit()
    return res

# 公共订阅源
@app.route('/api/v2/rss/pub',methods=['POST'])
@jwt_required()
def get_pub_rss():
    api_path = '/api/v2/rss/pub'
    return sync_post(api_path)


# 删除我的订阅
@app.route('/api/v2/my/rss/del',methods=['POST'])
@jwt_required()
def get_my_rss_del():
    api_path = '/api/v2/rss/add'
    data = request.get_json()
    res = sync_post(api_path)
    if res['data']['status'] == 'ok':
        user = User.query.filter(User.name == data['user_name']).get()
        user.feed_count = user.feed_count-1 if user.feed_count == 0 else 0
        db.session.add(user)
        db.session.commit()
    return res


def sync_post(path):
    data = request.get_json()
    if data:
        data['key'] = rss2ebook_key

    res = requests.post(config.RSS2EBOOK_URL+path, data=data, headers=headers)
    if res.status_code == 200:
        return APIResponse.success(json.loads(res.text))
    else:
        return APIResponse.bad_request(msg="调用接口错误")
