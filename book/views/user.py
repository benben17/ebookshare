# encoding:utf-8
import json
import time

from operator import or_

import requests
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

import config
from book import request, cache, app, db, User
from book.utils.ApiResponse import APIResponse
from book.utils import check_email, generate_code, model_to_dict
from book.utils.mailUtil import send_email


@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ['email', 'passwd']):
        return APIResponse.bad_request(msg="用户名密码为空！")

    user = User.query.filter(or_(User.name == data['email'], User.email == data['email'])).first()
    if user is None:
        return APIResponse.bad_request(msg="用户不存在")

    if not check_password_hash(user.hash_pass, data['passwd']):
        return APIResponse.bad_request(msg="密码不正确")

    user_info = model_to_dict(user)
    access_token = create_access_token(identity=user_info)
    data = {"user": user_info, "token": access_token}
    return APIResponse.success(data=data)


@app.route("/user/email/code/<email>")
def send_email_verification_code(email):
    if check_email(email):
        user = User.query.filter(or_(User.email == email, User.name == email)).first()
        if user:
            return APIResponse.bad_request(msg="该邮箱已注册，请直接登录。")
        else:
            verification_code = generate_code()
            cache.set(email, verification_code, timeout=300)
            send_email("RSS2EBOOK 验证码", verification_code, email)
            return APIResponse.success(msg="验证码已发送至您的邮箱，请查收。")
    else:
        return APIResponse.bad_request(msg="无效的邮箱地址！")


@app.route("/user/sign_up", methods=['POST'])
def sign_up():
    """POST /user/sign_up: user sign up handler
    """
    data = request.get_json()
    if not data.get('email') or not data.get('passwd'):
        return APIResponse.bad_request(msg="用户名密码为空！")

    email = data['email']
    passwd = data['passwd']
    if not check_email(email):
        return APIResponse.bad_request(msg="无效的邮箱地址！")

    user = User.query.filter(or_(User.email == email, User.name == email)).first()

    if user is None:
        user = User()
        user.id = str(int(time.time()))
        user.hash_pass = generate_password_hash(passwd)
        user.email = email
        user.name = user.email.split("@")[0]
        user.role = config.DEFAULT_USER_ROLE
        user.is_reg_rss = True
    else:
        if user.is_reg_rss:
            return APIResponse.bad_request(msg="此邮箱已注册！请直接登录")
    if sync_user(user):
        db.session.add(user)
        db.session.commit()
        user_info = model_to_dict(user)
        user_info['hash_pass'] = ""
        access_token = create_access_token(identity=user_info)
        data = {"user": user_info, "token": access_token}
        return APIResponse.success(data=data)
    else:
        return APIResponse.bad_request(msg="注册失败！")


@app.route('/user/forget/passwd', methods=['POST'])
@jwt_required()
def forget_passwd():
    data = request.get_json()
    user_name = data.get('email')
    if user_name:
        user = User.query.filter(or_(User.email == user_name, User.name == user_name)).first()
        if user:
            user.hash_pass = generate_password_hash(config.DEFAULT_USER_PASSWD)
            db.session.add(user)
            db.session.commit()
            send_email(f'{user_name} 重置密码', f'{user.email}:新密码为：{config.DEFAULT_USER_PASSWD}', user.email)
            return APIResponse.success(msg="密码重置成功，新密码发送至邮箱！")
        else:
            return APIResponse.bad_request(msg="用户不存在！")
    else:
        return APIResponse.bad_request(msg="用户名或邮箱地址为空！")


@app.route('/user/logout')
def logout():
    return APIResponse.success()


@app.route('/user/info')
@jwt_required()
def user_info():
    t_user = get_jwt_identity()
    user = User.query.get(t_user['id'])
    user.hash_pass = ""
    user_json = model_to_dict(user)
    access_token = create_access_token(identity=user_json)
    data = {"user": user_json, "token": access_token}
    return APIResponse.success(data=data)


@app.route('/user/update/<id>', methods=['GET', 'POST'])
def user_update(id):
    user = User.query.get(id)
    return APIResponse.success()


def sync_user(user):
    path = '/api/v2/sync/user/add'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user.name,
        'to_email': user.email,
        'expiration_days': '360'
    }
    res = requests.post(config.RSS2EBOOK_URL + path, data=data, headers=config.headers)
    if res.status_code == 200:
        res = json.loads(res.text)
        if res['status'].lower() == 'ok':
            return True
    return False
