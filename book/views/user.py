# encoding:utf-8
import json
import time
import requests
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.sql.operators import or_
from werkzeug.security import check_password_hash, generate_password_hash
import config
from book import cache
from book.dicts import UserRole
from book.models import db, User, UserPay
from flask import request, Blueprint
from book.utils.ApiResponse import APIResponse
from book.utils import check_email, generate_code, model_to_dict, get_file_name, get_rss_host
from book.utils.mailUtil import send_email

blueprint = Blueprint(
    get_file_name(__file__),
    __name__,
    url_prefix='/user'
)


@blueprint.route('/login', methods=['POST'])
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
    # print(user_info)
    access_token = create_access_token(identity=user_info)
    data = {"user": user_info, "token": access_token}
    return APIResponse.success(data=data)


@blueprint.route("/email/code/<email>")
def email_verify_code(email):
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


@blueprint.route("/sign_up", methods=['POST'])
def sign_up():
    """POST /user/sign_up: user sign up handler
    """
    data = request.get_json()
    if not data.get('email') or not data.get('passwd'):
        return APIResponse.bad_request(msg="邮箱或密码不允许为空！")

    email = data['email']
    passwd = data['passwd']
    if not check_email(email):
        return APIResponse.bad_request(msg="无效的邮箱地址！")

    user = User.query.filter(or_(User.email == email, User.name == email)).first()
    if user:
        return APIResponse.bad_request(msg="此邮箱已注册！请直接登录")
    user = User()
    user.id = int(time.time())
    user.hash_pass = generate_password_hash(passwd)
    user.email = email
    user.name = user.email.split("@")[0]
    user.kindle_email = email
    user.role = UserRole.role_name()
    user.is_reg_rss = True

    if sync_user(user):
        db.session.add(user)
        db.session.commit()
        user_info = model_to_dict(user)
        access_token = create_access_token(identity=user_info)
        data = {"user": user_info, "token": access_token}
        return APIResponse.success(data=data)
    else:
        return APIResponse.bad_request(msg="注册失败！")


@blueprint.route('/forget/passwd', methods=['POST'])
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


@blueprint.route('/logout')
def logout():
    return APIResponse.success()


@blueprint.route('/info')
@jwt_required()
def user_info():
    t_user = get_jwt_identity()
    user = User.query.get(t_user['id'])
    user_json = model_to_dict(user)
    access_token = create_access_token(identity=user_json)
    data = {"user": user_json, "token": access_token}
    return APIResponse.success(data=data)


@blueprint.route('/passwd/change', methods=['GET', 'POST'])
@jwt_required()
def user_passwd_change():
    data = request.get_json()
    user = get_jwt_identity()
    user_email = data['email']
    if user.email != user_email:
        return APIResponse.internal_server_error(msg="邮箱错误!")
    new_pass = data['passwd']
    user.hash_pass = generate_password_hash(new_pass)
    db.session.add(user)
    db.session.commit()
    return APIResponse.success(msg="密码修改成功！")


@blueprint.route('/pay/log', methods=['GET'])
@jwt_required()
def user_pay_log():
    user = get_jwt_identity()
    pay_logs = UserPay.query.filter_by(user_id=user['id']).all()
    user_pays = []
    for log in pay_logs:
        user_pays.append(model_to_dict(log))
    return APIResponse.success(data=user_pays)


def sync_user(user):
    path = '/api/v2/sync/user/add'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user.name,
        'to_email': user.email
    }
    res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS)
    if res.status_code == 200:
        res = json.loads(res.text)
        if res['status'].lower() == 'ok':
            return True
    return False




if __name__ == '__main__':
    print("a")
    from book import app
    from sqlalchemy import Enum
    with app.app_context():
        userpay  = UserPay.query.all()
        for pay in userpay:
            # model_to_dict()
            print(isinstance(pay.status,Enum))
        # passwd=generate_password_hash('admin')
        # user = User(name='admin',email='892100089@qq.com',hash_pass= passwd)
        # db.session.add(user)
        # db.session.commit()
        # log = UserPay.query.filter_by(status=PaymentStatus.completed).first()
        # print(log.user.email)
