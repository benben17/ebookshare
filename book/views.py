# encoding:utf-8
import hashlib
import time
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
import os
import config
from book import app,request
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
        if root.find('MsgType').text == 'text':
            content = root.find('Content').text
        else:
            content = "欢迎关注我的公众号"

        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        create_time = str(int(time.time()))
        from book.dbModels import Books
        books = Books.query.filter(Books.title.like(content)).all()
        msg_content = f'一共搜索到{len(books)}本书\n'
        if len(books) >0:
            for book in books:
                msg_content += f'{book.title} 作者:{book.author}\n'
        reply_xml = f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{create_time}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{msg_content}]]></Content>
        </xml>
        """
        return reply_xml

@app.route('/', methods=['GET', 'POST'])
def home():
    from book.dbModels import User
    user = User.query.filter(User.name == 'admin').first()
    return user.name
