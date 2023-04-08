import json
import logging

import requests
from flask import redirect, send_from_directory, render_template
from sqlalchemy import or_
from werkzeug.security import generate_password_hash
from book import request, cache, app, db, upgradeUser
from book.utils import *
from book.utils.wxMsg import *


@app.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 处理验证请求
        token = config.wechat_token
        echostr = request.args.get('echostr', '')
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        return echostr if check_signature(token, signature, timestamp, nonce) else ''

    elif request.method == 'POST':
        from book.dbModels import User, Userlog
        # 处理消息请求
        msg_type, from_user, to_user, content, event = parse_xml(request.data)
        from_user = from_user.strip()
        # logging.error(from_user)
        to_user = to_user.strip()
        if msg_type.strip() == 'event' and event.strip() == 'subscribe':
            return wx_reply_xml(from_user, to_user, reply_subscribe)
        elif msg_type.strip() == 'text':
            content = content.strip()
            # 查询用户
            if content.lower() in ['?', 'h', 'help', '帮助', '？']:
                return wx_reply_xml(from_user, to_user, reply_help_msg)
            elif content == '1002':
                return wx_reply_news(from_user, to_user)
            # 查找用户信息
            user = User.query.filter(User.wx_openid == from_user).first()
            if user is None:
                user = User()
            # 查询绑定的邮箱地址
            if content.lower() == "email":
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
            # 解绑
            if content == '1001':
                user_email = user.email
                if not user_email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                user.email = ""
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, unbind_email_msg(user_email))
            # 绑定邮箱
            if check_email(content):
                if user.email:
                    return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
                user_info = User.query.filter(or_(User.email == content, User.name == content,User.wx_openid == from_user)).first()
                if user_info:
                    if not user_info.wx_openid or user_info.wx_openid is None:
                        user_info.wx_openid = from_user
                elif user_info is None:
                    user_info = User()
                    user_info.email = content
                    user_info.kindle_email = content
                    user_info.wx_openid = from_user
                    user_info.hash_pass = generate_password_hash(config.DEFAULT_USER_PASSWD)
                    user_info.role = config.DEFAULT_USER_ROLE
                db.session.add(user_info)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))

            # 检查是不是 书籍ISBN
            if check_isbn(content):
                msg_content, books_cache = search_net_book(isbn=content, openid=from_user)
                if books_cache is not None:
                    cache.set_many(books_cache)  # 存缓存
                return wx_reply_xml(from_user, to_user, msg_content)
            # if content == 'next':
            if from_user == 'o6MX5t3TLA6Un9Mw7mM3nHGdOI-s' and content.startswith("upgrade"):
                info = content.split(":")
                if len(info) == 3:
                    upgrade_user = User.query.filter(or_(User.email == info[1], User.name == info[1])).first()
                    if upgrade_user:
                        upgradeUser.upgrade_user_thread(user, days=int(info[2]))
                        return wx_reply_xml(from_user, to_user, f"{upgrade_user.name}:用户升级中")
                return wx_reply_xml(from_user, to_user, "未找到用户，或者信息错误")

            # if content == "哈哈哈":
            #     return wx_reply_news(from_user, to_user)
            # 发送文件
            if re.match("[0-9]", content) and int(content) <= 16:
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                # 每个用户每天最多下载5本书
                usersend = Userlog.query.filter(Userlog.wx_openid == from_user, Userlog.status == 1,
                                                Userlog.create_time > get_now_date()).all()
                if len(usersend) > 5:
                    wx_reply_xml(from_user, to_user, "今天已经下载5本书，请明天在进行发送！")

                book_info = cache.get(f'{from_user}_{content}')
                if book_info is not None:
                    send_info = book_info.split(":")
                    logging.error(send_info)

                    user_log = Userlog(wx_openid=user.wx_openid, book_name=send_info[0], receive_email=user.email, user_id=user.id,
                                       operation_type='download', status=0, ipfs_cid=send_info[1],filesize=send_info[2])
                    db.session.add(user_log)
                    db.session.commit()
                    return wx_reply_xml(from_user, to_user, wx_reply_mail_msg(send_info[0], user.email))

                else:
                    return wx_reply_xml(from_user, to_user, reply_help_msg)

            # 搜索 图书
            msg_content, books_cache = search_net_book(title=content, openid=from_user)
            if books_cache is not None:
                cache.set_many(books_cache) #存缓存
            return wx_reply_xml(from_user, to_user, msg_content)

        else: # 其他未知消息
            return wx_reply_xml(from_user, to_user, reply_help_msg)


@app.route('/download/<path:filename>')
def dl(filename):
    if os.path.exists(os.path.join(config.DOWNLOAD_DIR,filename)) is False:
        return redirect("/404")
    return send_from_directory(config.DOWNLOAD_DIR, filename)
    # return APIResponse.success(data="欢迎关注 sendtokindles 公众号下载电子书")



class WeChat:
    def __init__(self):
        self.APPID = config.APPID
        self.APPSECRET= config.APPSECRET

    def get_token(self):

        token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'
        try:
            res = requests.get(token_url.format(self.APPID,self.APPSECRET))
            json_res = json.loads(res.text)
            if 'access_token' in json_res:
                # cache.add('access_token',json_res['access_token'])
                return json_res['access_token']
        except Exception as e:
            logging.error("获取token 失败！："+e)
    def create_menu(self):
        ACCESS_TOKEN = self.get_token()
        create_menu_button_url= f'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={ACCESS_TOKEN}'
        my = "http://www.baidu.com"
        param = '''{
            "button": [
                {
                    "type": "click",
                    "name": "个人中心",
                    "key": "{my}"
                },
                {
                    "name": "菜单",
                    "sub_button": [
                        {
                            "type": "view",
                            "name": "搜索",
                            "url": "http://www.soso.com/"
                        },
                        {
                            "type": "click",
                            "name": "赞一下我们",
                            "key": "V1001_GOOD"
                        }]
                }]
        }'''
        param.format(my)
        requests.post(create_menu_button_url,param)

        try:
            print("a")
        except Exception as e:
            print(e)
if __name__ == '__main__':
    with app.app_context():
        from book.dbModels import User
        content = '892100089@qq.com'
        user_info = User.query.filter(or_(User.email==content,User.name==content)).first()
        print(user_info.name)