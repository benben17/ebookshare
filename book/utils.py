# -*-coding: utf-8-*-
import os.path
import re
import time, os
from pathlib import Path


no_bind_email_msg = '''你好，你还没有绑定邮箱,请发送[ email#邮箱地址 ] 进行绑定\n
\n
例如：email#book@book.com\n'''

reply_help = '''请输入文字信息！\n
回复 ? help h H 帮助信息\n
回复email绑定邮箱\n
回复你想搜索的书籍名字进行搜索\n
回复图书编号可直接发送到邮箱'''

def checkemail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.findall(pattern, email):
        return True
    else:
        return False


def wx_reply_xml(from_user, to_user, msg_content):
    """
    desc: 微信回复消息模版
    :param from_user: 发送人
    :param to_user: 接受人
    :param msg_content: 接收消息内容
    :return:
    """
    create_time = str(int(time.time()))
    return f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{create_time}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{msg_content}]]></Content>
        </xml>
        """


def allowed_file(filename):
    """
    :param filename: 带路径的文件
    :return:
    """
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_ebook_ext(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'mobi', 'azw3', 'epub'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_name(file):
    file_suffix = str(Path(file).suffix)
    return os.path.basename(file).replace(file_suffix, "")


def get_file_suffix(file):
    if '.' in file:
        _, suffix = file.rsplit('.', 1)
        return suffix.lower()

