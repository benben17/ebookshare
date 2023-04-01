# encoding:utf-8
import hashlib
import logging
import os.path
import re

import config
from book import request, cache, parse_xml, app, check_isbn, search_net_book
from book.dbModels import db
from book.wxMsg import *



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
        from book.dbModels import User, Userlog, Books
        # 处理消息请求
        msg_type, from_user, to_user, content, event = parse_xml(request.data)
        from_user = from_user.strip()
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
                user = User(wx_openid=from_user)
                db.session.add(user)
                db.session.commit()
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
            if checkemail(content):
                if user.email:
                    return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
                user.email = content
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
            if check_isbn(content):
                return wx_reply_xml(from_user, to_user, not_isbn_search)
            # 发送文件
            if re.match("[0-9]", content) and len(content) == 1 and int(content) <= 11:
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                # user_log = Userlog.query.filter(Userlog.user_id == from_user,Userlog.create_time >= ).all()
                # if len(user_log) >= 5:
                #     return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
                book_info = cache.get(f'{from_user}_{content}')
                if book_info is not None:
                    send_info = book_info.split(":")
                    logging.error(send_info)
                    userlog = Userlog.query.filter(Userlog.book_name == send_info[0],Userlog.ipfs_cid == send_info[1],Userlog.status == config.FAILED_FlAG).all()
                    if userlog:
                        return wx_reply_xml(from_user, to_user, send_failed_msg)
                    user_log = Userlog(user_id=user.id, book_name=send_info[0], receive_email=user.email,
                                       operation_type='download', status=0, ipfs_cid=send_info[1])
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

@app.route('/', methods=['GET', 'POST'])
def home():
    return "hello"
