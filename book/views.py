# encoding:utf-8
import hashlib
import logging
import xml.etree.ElementTree as ET
import config
from book import wx_reply_xml, request, no_bind_email_msg, checkemail, bind_email_msg
from book.dbModels import *


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
        content = root.find('Content').text
        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        logging.error(f'from_user:{from_user} to_user:{to_user}')
        # 查询用户
        from book.dbModels import User
        user = User.query.filter_by(wx_openid=from_user).first()
        if user is None:
            user = User(wx_openid=from_user)
            db.session.add(user)
            db.session.commit()
        if not user.email:
            # 绑定邮箱
            if content.lower().startswith("email"):
                str_text = content.split("#")
                if len(str_text) == 2 and checkemail(str_text[1]):
                    user.email = str_text[1]
                    db.session.commit()
                    wx_reply_xml(from_user, to_user, bind_email_msg.format(str_text[1]))
            if checkemail(content):
                user.email = content
                db.session.commit()
                wx_reply_xml(from_user, to_user, bind_email_msg.format(content))
        else:
            return wx_reply_xml(from_user, to_user, no_bind_email_msg)

        from book.dbModels import Books
        books = Books.query.filter(Books.title.like(f'%{content}%')).all()
        msg_content = f'一共搜索到{len(books)}本书\n'
        for book in books:
            author = book.author if book.author is not None else ""
            msg_content += f'《{book.title}》作者:{author} \n'
        return wx_reply_xml(from_user, to_user, msg_content)


@app.route('/', methods=['GET', 'POST'])
def home():
    return "hello"
