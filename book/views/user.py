# encoding:utf-8
from datetime import datetime, timedelta
import json
import requests
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.sql.operators import or_
from werkzeug.security import check_password_hash, generate_password_hash
import config
from book import cache
from book.dateUtil import format_time
from book.dicts import UserRole, PaymentStatus
from book.models import db, User, UserPay
from flask import request, Blueprint
from book.utils.ApiResponse import APIResponse
from book.utils import check_email, generate_code, model_to_dict, get_file_name, get_rss_host, gen_userid
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
    # 修复公众号用户
    if not user.hash_pass and  not user.is_reg_rss:
        user.hash_pass = generate_password_hash(data["passwd"])
        user.name = user.email.split("@")[0] if not user.name else user.name
        send_email(f'{user.email} passwd', f'password:{data["passwd"]}\n first login', data['email'])
        if sync_user(user):
            user.role = UserRole.role_name('default')
            user.is_reg_rss = True
            db.session.add(user)
            db.session.commit()

    if not check_password_hash(user.hash_pass, data['passwd']):
        return APIResponse.bad_request(msg="密码不正确")

    userinfo = model_to_dict(user)
    access_token = create_access_token(identity=userinfo)
    data = {"user": userinfo, "token": access_token}
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
    user.id = gen_userid()
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
    pay_logs = UserPay.query.filter_by(user_id=user['id']).order_by(UserPay.create_time.desc()).all()
    user_pays = []
    for log in pay_logs:
        refund_flag = False
        if log.pay_time and log.status == PaymentStatus.completed:
            refund_time = log.pay_time + timedelta(weeks=2)  # 2周后的日期
            refund_flag = refund_time > datetime.utcnow()
        log = model_to_dict(log)
        log['pay_time'] = format_time(log['pay_time'])
        log['create_time'] = format_time(log['create_time'])
        log['refund_flag'] = refund_flag
        user_pays.append(log)
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
    from sqlalchemy import Enum, desc

    with app.app_context():
        content = '892100089@qq.com'

        user = User().query.filter_by(wx_openid="content").first()
        if user and user.email:
            print(user.email)
        elif user and user.email is None:
            user.email = content
            db.session.add(user)
        elif not user:  # 通过openID 没有查询到用户
            user_info = User.query.filter(or_(User.email == content, User.kindle_email == content)).first()
            if user_info and not user_info.wx_openid:
                print(user_info.wx_openid)
                user_info.wx_openid = "content"
                db.session.add(user_info)
            elif not user_info:
                user_info = User(email=content, kindle_email=content, wx_openid="content")
                db.session.add(user_info)
        db.session.commit()
