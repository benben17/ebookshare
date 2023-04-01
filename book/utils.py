# -*-coding: utf-8-*-
import hashlib
import os.path
import re
import time, os
from pathlib import Path
import xml.etree.ElementTree as ET

import config


def parse_xml(xml_str):
    """解析xml字符串"""
    root = ET.fromstring(xml_str)
    msg_type = root.findtext('MsgType')
    from_user = root.findtext('FromUserName')
    to_user = root.findtext('ToUserName')
    content = root.findtext('Content')
    event = root.findtext('Event')
    return msg_type, from_user, to_user, content, event


def search_book_content(books, from_user):
    if len(books) == 0:
        msg_content = f'你搜的书不存在，请尝试搜索其他书籍！\n'
        return msg_content,None
    msg_content = f'一共搜索到{len(books)}本书:\n'
    books_cache = {}
    row_num = 1
    for book in books:
        if book.bookext.book_download_url is None:
            continue
        author = book.author if book.author is not None else ""
        msg_content += f'{row_num} :{book.title}-{author} \n'
        books_cache[f'{from_user}_{row_num}'] = f'{book.title}:{book.bookext.book_download_url}'
        row_num += 1
    msg_content += f'发送图书编号直接发送到绑定邮箱。\n'
    return msg_content, books_cache


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
    if isinstance(file, str) and '.' in file:
        _, suffix = file.rsplit('.', 1)
        return suffix.lower()
    return None


def filesize_format(value, binary=False):
    " bugfix for do_filesizeformat of jinja2 "
    bytes = float(value)
    base = 1024 if binary else 1000
    prefixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    for i, prefix in enumerate(prefixes):
        unit = base ** i
        if bytes < base ** (i + 1):
            return f"{bytes / unit:.1f} {prefix}"
    return f"{bytes / unit:.1f} {prefixes[-1]}"


