# encoding:utf-8
import hashlib
import logging
import os.path
import re
import xml.etree.ElementTree as ET
import config
from book import request,  send_email, cache
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
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if signature == hashlib.sha1(s.encode('utf-8')).hexdigest():
            return echostr
        else:
            return ''
    else:
        # 处理消息请求
        xml_data = request.data
        root = ET.fromstring(xml_data)

        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        if root.find("MsgType").text == 'event':
            if root.find("Event") == 'subscribe':
                return wx_reply_xml(from_user, to_user, reply_subscribe)

        if root.find('MsgType').text != 'text':
            return wx_reply_xml(from_user, to_user, reply_help_msg)
        content = root.find('Content').text
        logging.error(f'from_user:{from_user} to_user:{to_user}')
        if content == '1002':
            return wx_reply_news(from_user, to_user)
        # 查询用户

        if content.lower() in ['?', 'h', 'help', '帮助', '？']:
            return wx_reply_xml(from_user, to_user, reply_help_msg)

        from book.dbModels import User
        user = User.query.filter(User.wx_openid == from_user).first()
        if user is None:
            user = User(wx_openid=from_user)
            db.session.add(user)
            db.session.commit()
            user = User.query.filter(User.wx_openid == from_user).first()

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

        if not user.email:
            # 绑定邮箱
            if checkemail(content):
                logging.error(content)
                user.email = content
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, f'你好，你已经绑定绑定邮箱:{content}')
            return wx_reply_xml(from_user, to_user, no_bind_email_msg)

        # 发送文件
        if re.match("[0-9]",content) and len(content) == 1 and int(content) <= 11:
            book_info = cache.get(f'{from_user}_{content}')
            if book_info is not None:
                send_info = book_info.split(":")
                logging.error(send_info)
                book_file = config.BOOK_FILE_DIR+send_info[1]
                book_name = send_info[0]
                # logging.error("路径:"+book_file)
                if os.path.exists(book_file):
                    send_email(book_name, book_name, user.email, book_file)
                    user_log = Userlog(user_id=user.id, book_name=book_name, receive_email=user.email,operation_type='download')
                    db.session.add(user_log)
                    db.session.commit()
                    return wx_reply_xml(from_user, to_user,wx_reply_mail_msg(book_name, user.email))
                else:
                    return wx_reply_xml(from_user, to_user, f"{book_name} 不存在！")
            else:
                return wx_reply_xml(from_user, to_user, reply_help_msg)

        from book.dbModels import Books
        books = Books.query.filter(Books.title.like(f'%{content}%')).limit(10).all()
        msg_content = f'一共搜索到{len(books)}本书\n'
        find_books = {}
        row_num = 1
        for book in books:
            if book.bookext.book_download_url is None:
                continue
            author = book.author if book.author is not None else ""
            msg_content += f'{row_num} :《{book.title}》作者:{author} \n'
            find_books[f'{from_user}_{row_num}'] = f'{book.title}:{book.bookext.book_download_url}'
            row_num += 1
        msg_content += f'发送图书编号直接发送到绑定邮箱\n'
        cache.set_many(find_books)
        return wx_reply_xml(from_user, to_user, msg_content)


@app.route('/', methods=['GET', 'POST'])
def home():
    return "hello"
