import json
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
import config
from book import app, request, User, db
from book.utils.ApiResponse import APIResponse

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


# 用户同步
@app.route('/api/v2/sync/user/add', methods=['POST'])
def user_add():
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


# 用户设置
@app.route('/api/v2/sync/user/seting', methods=['POST'])
@jwt_required()
def user_setting():
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/sync/user/upgrade', methods=['POST'])
@jwt_required()
def user_upgrade():
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/sync/user/info', methods=['POST'])
@jwt_required()
def rss_user_info():
    res = sync_post(request.path)
    if res['status'] == "ok":
        print(res['data'])
        # print(type(res['data']))
        user_info = res['data']
        return APIResponse.success(data=user_info)
    else:
        return APIResponse.bad_request(msg=res['msg'])


# 获取发送日志
@app.route('/api/v2/my/deliver/logs', methods=['POST'])
@jwt_required()
def get_deliver_logs():
    res = sync_post(request.path)
    if res['status'] == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/feed/book/deliver', methods=['POST'])
@jwt_required()
def get_my_feed_deliver():
    res = sync_post(request.path)
    if res['status'] == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/my/rss', methods=['POST'])
@jwt_required()
def rss_my():
    api_path = '/api/v2/rss/myrss'
    res = sync_post(api_path)
    if res['status'].lower() == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/my/rss/add', methods=['POST'])
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


# 公共订阅源
@app.route('/api/v2/rss/pub', methods=['POST'])
@jwt_required()
def get_pub_rss():
    api_path = '/api/v2/rss/pub'
    res = sync_post(api_path)
    if res['status'] == "ok":
        return APIResponse.success(data=res['data'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


# 删除我的订阅
@app.route('/api/v2/my/rss/del', methods=['POST'])
@jwt_required()
def my_rss_del():
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


@app.route('/api/v2/rss/share', methods=['POST'])
@jwt_required()
def rss_share():
    res = sync_post(request.path)
    if res['status'].lower() == "ok":
        return APIResponse.success(msg=res['msg'])
    else:
        return APIResponse.bad_request(msg=res['msg'])


@app.route('/api/v2/rss/invalid', methods=['POST'])
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
    request_url = config.RSS2EBOOK_URL
    # request_url = "http://127.0.0.1:8080"
    res = requests.post(request_url + path, data=data, headers=headers, timeout=60)
    # print(res.content)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        if json_data['status'] == "ok":
            return json_data
        return {"status": "failed", "msg": res.content}
    else:
        return {"status": "failed", "msg": res.content}
