# encoding:utf-8
import logging
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
from sqlalchemy.sql.operators import or_
from werkzeug.security import check_password_hash, generate_password_hash
from book.utils.commUtil import cacheKey
from book import cache
from book.dicts import UserRole, PaymentStatus
from book.models import db, User, UserPay, Advice
from flask import request, Blueprint
from book.utils.ApiResponse import APIResponse
from book.utils import check_email, generate_code, model_to_dict, get_file_name, gen_userid, commUtil
from book.utils.commUtil import sync_user, new_passwd
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
        return APIResponse.bad_request(msg="Username or Password is empty！")

    user = User.query.filter(or_(User.email == data['email'], User.name == data['email'])).first()
    if user is None:
        return APIResponse.bad_request(msg=f"User :{data['email']} is not exists!")
    # 修复公众号用户
    if not user.hash_pass and not user.is_reg_rss:
        user.hash_pass = generate_password_hash(data["passwd"])
        user.name = user.email.split("@")[0] if not user.name else user.name
        send_email(f'{user.email} passwd', f'password:{data["passwd"]}\n first login', data['email'])
        if sync_user(user):
            user.role = UserRole.role_name('default')
            user.is_reg_rss = True
            db.session.add(user)
            db.session.commit()

    if not check_password_hash(user.hash_pass, data['passwd']):
        return APIResponse.bad_request(msg="Incorrect password!")

    userinfo = model_to_dict(user)
    access_token = create_access_token(identity=userinfo)
    data = {"user": userinfo, "token": access_token}
    return APIResponse.success(data=data)


@blueprint.route("/email/code/<email>")
def email_verify_code(email):
    if check_email(email):
        user = User.query.filter(or_(User.email == email, User.name == email)).first()
        if user:
            return APIResponse.bad_request(msg="该邮箱已注册，请直接登录。忘记密码请使用找回密码！")
        else:
            verification_code = generate_code()
            cache.set(email, verification_code, timeout=300)
            send_email("RSS2EBOOK 注册验证码", 'RSS2EBOOK 注册验证码： ' + verification_code, email)
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
    user.create_time = datetime.utcnow()

    if commUtil.sync_user(user):
        db.session.add(user)
        db.session.commit()
        user_info = model_to_dict(user)
        access_token = create_access_token(identity=user_info)
        data = {"user": user_info, "token": access_token}
        return APIResponse.success(data=data)
    else:
        return APIResponse.bad_request(msg="注册失败！")


@blueprint.route('/reset/passwd', methods=['POST'])
def forget_passwd():
    email = request.get_json().get('email')
    code = request.get_json().get('code')

    if not email or not code:
        return APIResponse.bad_request(msg="Email or Code is empty！")
    try:
        cacheKey = cacheKey.resetKey.format(email)
        sys_code = cache.get(cacheKey)
        if sys_code is None or str(sys_code) != str(code):
            return APIResponse.bad_request(msg='验证码错误！')
        user = User.query.filter(User.email == email).first()
        if not user:
            return APIResponse.bad_request(msg="user not exists！")
        new_pass = new_passwd()
        user.hash_pass = generate_password_hash(new_pass)
        logging.info(f"passwd:{new_pass}:{user.hash_pass}")
        db.session.add(user)
        db.session.commit()
        send_email(f'{user.email} Password Reset', f'{user.email}:New Password ：{new_pass}',
                   user.email)
        logging.info(f"111passwd:{new_pass}")
        return APIResponse.success(msg="Password reset successful，New password sent to email!")
    except Exception as e:
        logging.error(f'Password Reset error:{str(e)}')
        return APIResponse.bad_request(msg="Password Reset error")


@blueprint.route("/forget/code", methods=['GET'])
def email_forget_code():
    email = request.args.get('email')
    if check_email(email) is False:
        return APIResponse.bad_request(msg="Invalid email address！")

    cacheKey = cacheKey.sendCount.format(email)

    send_count = 0 if not cache.get(cacheKey) else int(cache.get(cacheKey))
    if send_count >= 6:
        return APIResponse.bad_request(msg="Sent many times, please send it after 10 minutes")
    send_count += 1
    user = User.query.filter(or_(User.email == email, User.name == email)).first()
    if not user:
        return APIResponse.bad_request(msg="user not exists or error")
    verification_code = generate_code()
    cache.set(cacheKey.resetKey.format(email), verification_code, timeout=600)
    cache.set(cacheKey, send_count, timeout=600)
    logging.info(f'code:{verification_code}')
    send_email("RSS2EBOOK Password reset code",
               f'RSS2EBOOK \n Account: {email} reset \n password reset Code： {verification_code}', email)
    return APIResponse.success(msg="验证码已发送至您的邮箱，请查收。")


@blueprint.route('/logout')
def logout():
    return APIResponse.success()


@blueprint.route('/info')
@jwt_required()
def user_info():
    t_user = get_jwt_identity()
    user = User.query.get(t_user['id'])
    user_json = model_to_dict(user)
    access_token = ''  # create_access_token(identity=user_json)
    data = {"user": user_json, "token": access_token}
    return APIResponse.success(data=data)


@blueprint.route('/passwd/change', methods=['GET', 'POST'])
@jwt_required()
def user_passwd_change():
    data = request.get_json()

    new_pass = data.get('passwd')
    user = User.get_by_id(int(get_jwt_identity()['id']))
    if not user or not new_pass:
        return APIResponse.bad_request(msg="user not exists or password is empty!")

    user.hash_pass = generate_password_hash(new_pass)
    db.session.add(user)
    db.session.commit()
    return APIResponse.success(msg="Change password successful")


@blueprint.route('/pay/log', methods=['GET'])
@jwt_required()
def user_pay_log():
    u = get_jwt_identity()
    pay_logs = UserPay.query.filter_by(user_id=u['id']).order_by(UserPay.create_time.desc()).all()
    user_pays = []
    tz = User.get_tz(u['id'])
    for log in pay_logs:
        refund_flag = False
        if log.pay_time and log.status == PaymentStatus.completed:
            refund_time = log.pay_time + timedelta(weeks=2)  # 2周后的日期
            refund_flag = refund_time > datetime.utcnow()
        log = model_to_dict(log, tz=tz)
        log['refund_flag'] = refund_flag
        user_pays.append(log)
    return APIResponse.success(data=user_pays)


@blueprint.route('/advice', methods=['POST'])
@jwt_required()
def advice():
    data = request.get_json()
    userinfo = get_jwt_identity()
    advice = Advice(user_name=userinfo['name'], user_email=userinfo['email'], content=data['content'])
    db.session.add(advice)
    db.session.commit()
    return APIResponse.success(msg='Thanks for your advice.')


if __name__ == '__main__':
    print("a")
    "pbkdf2:sha256:260000$18OgiuayUI0qk0NZ$c0c08f9505e4d296146a9a4e25404f3ef075c16737f3efd1ddf979e19344b2de"
    hash_pass = "pbkdf2:sha256:260000$8aQWKgTw7XFUFVsq$9dfa2bc7ea608f1c1f4b1e1d5af1fca6ce970e3aac7dc6678aa2b9b34ef5913c"
    pa = "uJ4eA3s4"
    print(check_password_hash(hash_pass, pa))
    # with app.app_context():
    #     content = '892100089@qq.com'
    #
    #     user = User().query.filter_by(wx_openid="content").first()
    #     if user and user.email:
    #         print(user.email)
    #     elif user and user.email is None:
    #         user.email = content
    #         db.session.add(user)
    #     elif not user:  # 通过openID 没有查询到用户
    #         user_info = User.query.filter(or_(User.email == content, User.kindle_email == content)).first()
    #         if user_info and not user_info.wx_openid:
    #             print(user_info.wx_openid)
    #             user_info.wx_openid = "content"
    #             db.session.add(user_info)
    #         elif not user_info:
    #             user_info = User(email=content, kindle_email=content, wx_openid="content")
    #             db.session.add(user_info)
    #     db.session.commit()
