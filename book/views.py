# encoding:utf-8
import hashlib
import logging
import os.path
import re

import config
from book import request, send_email, cache, parse_xml, search_book_content
from book.dbModels import *
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
        if check_signature(token, signature, timestamp, nonce):
            return echostr
        else:
            return ''
    elif request.method == 'POST':
        # 处理消息请求
        msg_type, from_user, to_user, content, event = parse_xml(request.data)
        from_user = from_user.strip()
        to_user = to_user.strip()
        if msg_type.strip() == 'event' and event.strip() == 'subscribe':
            return wx_reply_xml(from_user, to_user, reply_subscribe)
        elif msg_type.strip() == 'text':
            content = content.strip()
            logging.error(f'from_user:{from_user} to_user:{to_user}')
            # 查询用户
            if content.lower() in ['?', 'h', 'help', '帮助', '？']:
                return wx_reply_xml(from_user, to_user, reply_help_msg)
            elif content == '1002':
                return wx_reply_news(from_user, to_user)
            from book.dbModels import User
            user = User.query.filter(User.wx_openid == from_user).first()
            if user is None:
                user = User(wx_openid=from_user)
                db.session.add(user)
                db.session.commit()

            # 查询绑定的邮箱地址
            if content.lower() == "email":
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                return wx_reply_xml(from_user, to_user, f'你好，你绑定邮箱:{user.email}')
            if content == '1001':
                user_email = user.email
                if not user_email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                user.email = ""
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, f'你好，你已经解绑邮箱:{user_email}')
            # 绑定邮箱
            if checkemail(content):
                if user.email:
                    return wx_reply_xml(from_user, to_user, f'你好，你已经解绑邮箱:{user.email}')
                user.email = content
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, f'你好，你已经绑定绑定邮箱:{content}')
            # 发送文件
            if re.match("[0-9]", content) and len(content) == 1 and int(content) <= 11:
                book_info = cache.get(f'{from_user}_{content}')
                if book_info is not None:
                    send_info = book_info.split(":")
                    logging.error(send_info)
                    book_file = config.BOOK_FILE_DIR + send_info[1]
                    book_name = send_info[0]
                    # logging.error("路径:"+book_file)
                    if os.path.exists(book_file):
                        send_email(book_name, book_name, user.email, book_file)
                        user_log = Userlog(user_id=user.id, book_name=book_name, receive_email=user.email,
                                           operation_type='download')
                        db.session.add(user_log)
                        db.session.commit()
                        return wx_reply_xml(from_user, to_user, wx_reply_mail_msg(book_name, user.email))
                    else:
                        return wx_reply_xml(from_user, to_user, f"{book_name} 不存在！")
                else:
                    return wx_reply_xml(from_user, to_user, reply_help_msg)
            # 搜索 图书
            from book.dbModels import Books
            books = Books.query.filter(Books.title.like(f'%{content}%')).limit(10).all()
            msg_content, books_cache = search_book_content(books,from_user)
            cache.set_many(books_cache)
            return wx_reply_xml(from_user, to_user, msg_content)
        else: # 其他未知消息
            return wx_reply_xml(from_user, to_user, reply_help_msg)


@app.route('/', methods=['GET', 'POST'])
def home():
    return "hello"
