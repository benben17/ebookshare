# encoding:utf-8
import hashlib
from datetime import time
from urllib import request
import xml.etree.ElementTree as ET
import config
from book import app, WeChat


@app.route('/')
def hello_world():  # put application's code here
    return config.APPID


@app.route('wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 处理验证请求
        token = WeChat().get_token()
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
        msg_type = root.find('MsgType').text
        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        content = root.find('Content').text

        reply_xml = f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{str(int(time.time()))}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{content}]]></Content>
        </xml>
        """
        return reply_xml
