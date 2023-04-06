# encoding:utf-8
import hashlib

import os
from operator import or_
from flask import redirect, render_template, g, flash, current_app, url_for
from sqlalchemy.sql.functions import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from book import request, cache, app, db, User
from flask_principal import Identity, identity_changed, RoleNeed
from book.ApiResponse import APIResponse
from book.form import UserForm, LoginForm, ForgetPasswdForm
from book.utils import check_email, generate_code
from book.mailUtil import send_email

# @app.before_request
# def before_request():
#     g.user = current_user


@app.route("/")
def home():
    # logging.error(app.template_folder)
    return "欢迎关注公众号：sendtokindles 下载电子书"

@app.before_request
def before_request():
    g.user = current_user

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    user = User.query.filter(or_(User.name == form.name.data, User.email == form.name.data)).first()
    if user is not None:
        if check_password_hash(user.hash_pass, form.passwd.data):
            login_user(user)
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
            return redirect('dashboard')
        else:
            flash(u'密码不正确！')
    else:
        flash(u'用户不存在！')
    return render_template('login.html',form=form)


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


@app.route("/user/sign_up")
def sign_up():
    """GET|POST /create-account: create account form handler
    """
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.email == form.email.data, User.name == form.email.data)).first()
        if user:
            return flash("此邮箱已注册，请直接登录！")
        # add user to database
        u = User(email=form.email.data,
                 password=generate_password_hash(form.password.data))
        db.session.add(u)
        db.session.flush()

        # send verification email
        # send_verification_email(u)
        # login user
        login_user(u, remember=True)
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(u.id))

        return redirect(request.args.get('next') or url_for('content.home'))

    return render_template('/user/sign_up.html', form=form)


@app.route('/user/forget/passwd')
def forget_passwd():
    form = ForgetPasswdForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.email == form.email.data, User.name == form.email.data)).first()
        verify_code = cache.get(form.email.data)
        if verify_code != form.email_code:
            flash("验证码错误！")
        user.hash_pass = generate_password_hash(form.passwd.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template('forget_passwd.html', form=form)
