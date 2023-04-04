import requests
import config
from book import app, request, Blueprint
from flask import jsonify

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

rss2ebook_key = 'rss2Ebook.com.luck!'
# 用户同步
@app.route('/api/v2/sync/user/add',  methods=['POST'])
def user_add():
    return sync_post(request.path)

# 用户设置
@app.route('/api/v2/sync/user/seting',  methods=['POST'])
def user_setting():
    return jsonify(request.path)

@app.route('/api/v2/sync/user/upgrade',  methods=['POST'])
def user_upgrade():
    return sync_post(request.path)

# 获取发送日志
@app.route('/api/v2/my/deliver/logs',methods=['POST'])
def get_deliver_logs():
    return jsonify(sync_post(request.path))

@app.route('/api/v2/feed/book/deliver',methods=['POST'])
def get_my_feed_deliver():
    return sync_post(request.path)

@app.route('/api/v2/my/rss/add',methods=['POST'])
def get_my_rss_add():
    api_path = '/api/v2/rss/add'
    return sync_post(api_path)

@app.route('/api/v2/my/rss/del',methods=['POST'])
def get_my_rss_del():
    api_path = '/api/v2/rss/del'
    return sync_post(api_path)

def sync_post(path):
    data = request.get_json()
    if data:
        data['key'] = rss2ebook_key
    res = requests.post(config.RSS2EBOOK_URL+path, data=data, headers=headers)
    return res.text
