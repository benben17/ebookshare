# encoding:utf-8
import hashlib
import logging

import os
from operator import or_
from flask import redirect, flash
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

import config
from book import request, cache, app, db, User
from book.ApiResponse import APIResponse
from book.utils import check_email, generate_code, model_to_dict
from book.mailUtil import send_email


@app.route("/")
def home():
    # logging.error(app.template_folder)
    return "欢迎关注公众号：sendtokindles 下载电子书"



@app.route('/login', methods = ['GET', 'POST'])
def login():
    data = request.get_json()
    if data['email'] and data['passwd']:
        user = User.query.filter(or_(User.name == data['email'], User.email == data['email'])).first()
        if user is not None:
            if check_password_hash(user.hash_pass, data['passwd']):
                user_info = model_to_dict(user)
                access_token = create_access_token(identity=user_info)
                data = {"user":user_info,"token":access_token}
                return APIResponse.success(data=data)
            else:
                APIResponse.bad_request(data="密码不正确")
        else:
            APIResponse.bad_request(data="用户不存在")
    return APIResponse.bad_request(msg="用户名密码为空！")


@app.route("/email/code/<email>")
def mail_code(email):
    print(check_email(email))
    if check_email(email) is True:
        user = User.query.filter(or_(User.email == email, User.name == email)).first()
        if user:
            return APIResponse.bad_request(msg="邮箱已注册,请直接登录。")
        else:
            verify_mail_code = generate_code()
            cache.set(email, verify_mail_code, timeout=300)
            send_email("注册rss2ebook验证码", verify_mail_code, email)
    return APIResponse.bad_request(msg="邮箱错误！")


@app.route("/user/sign_up",methods = ['GET', 'POST'])
def sign_up():
    """GET|POST /create-account: create account form handler
    """
    data = request.get_json()
    if data['email'] and data['passwd']:
        user = User.query.filter(or_(User.email == data['email'], User.name == data['email'])).first()
        if user:
            APIResponse.bad_request(msg="此邮箱已注册，请直接登录！")


        logging.error(generate_password_hash(data['passwd']))
        user = User()
        user.hash_pass = generate_password_hash(data['passwd'])
        user.email = data['email']
        user.name = user.email.split("@")[0]
        user.role = config.DEFAULT_USER_ROLE
        db.session.add(user)
        db.session.commit()
        user_info = model_to_dict(user)
        access_token = create_access_token(identity=user_info)
        data = {"user": user_info, "token": access_token}
        return APIResponse.success(data=data)

    return APIResponse.bad_request(msg="用户名密码为空！")


@app.route('/user/forget/passwd')
@jwt_required()
def forget_passwd():
    data = request.get_json()
    if data['user_name']:
        user = User.query.filter(or_(User.email == data['user_name'], User.name == data['user_name'])).first()
        user.hash_pass = generate_password_hash(data['passwd'])
        db.session.add(user)
        db.session.commit()
        send_email(f'{data["user_name"]}重置密码', user.hash_pass, user.email)
        return APIResponse.success()
    return APIResponse.bad_request(msg="用户名不允许为空")

@app.route('/logout')

def logout():


    return APIResponse.success()



@app.route('/user/update/<id>', methods = ['GET', 'POST'])
def user_update(id):
    user = User.query.get(id)
    return APIResponse.success()
