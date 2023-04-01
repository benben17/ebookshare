# -*-coding: utf-8-*-

import logging
import os.path
import time, os
from pathlib import Path
import xml.etree.ElementTree as ET
import isbnlib
import requests
from requests.exceptions import RequestException

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
        msg_content += f'{row_num} :【{book.title}】.{book.extension}】-{author} \n'
        books_cache[f'{from_user}_{row_num}'] = f'{book.title}:{book.bookext.book_download_url}'
        row_num += 1
    msg_content += '---------------------------\n'
    msg_content += f'发送图书编号直接发送到绑定邮箱。\n'
    return msg_content, books_cache

def allowed_file(filename):
    """
    :param filename: 带路径的文件
    :return:
    """
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_isbn(str):
    if len(str) == 13:
        return isbnlib.is_isbn13(str)
    elif len(str) == 10:
        return isbnlib.is_isbn10(str)
    else:
        return False

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


def net_book_content(books, from_user):
    if len(books) == 0:
        msg_content = f'你搜的书不存在，请尝试搜索其他书籍！\n'
        return msg_content,None
    msg_content = f'一共搜索到{len(books)}本书:\n'
    books_cache = {}
    row_num = 1
    for book in books:
        author = book['author'] if book['author'] is not None else ""
        title = book['title']
        ext = book['extension']
        ipfs_cid = book['ipfs_cid']
        filename = f'{title}.{ext}'
        msg_content += f'{row_num} :【{title}.{ext}】-{author} \n'
        books_cache[f'{from_user}_{row_num}'] = f'{filename}:{ipfs_cid}'
        row_num += 1
    msg_content += '---------------------------\n'
    msg_content += f'发送图书编号直接发送到绑定邮箱。\n'
    return msg_content, books_cache

def search_net_book(title=None,author=None,isbn=None, openid=""):
    search_url = 'https://zlib.knat.network/search?limit=10&query='
    if not any((title, author, isbn)):
        return None
    param = ''
    if title is not None:
        param += f'title:"{title}"'
    if author is not None:
        param += f'author:"{author}"'
    if isbn is not None:
        param += f'isbn:"{isbn}"'
    res = requests.get(url=search_url+param, timeout=30)
    if int(res.status_code) == 200:
        json_res = res.json()
        return net_book_content(json_res['books'],openid)
    return False




def download_net_book(ipfs_cid, filename):
    url_list = [
        'https://ipfs.io',
        'https://cloudflare-ipfs.com',
        'https://dweb.link',
        'https://gateway.pinata.cloud'
    ]

    for url in url_list:
        url_with_cid = f"{url}/ipfs/{ipfs_cid}?filename={filename}"
        logging.info(ipfs_cid)
        logging.info(filename)

        try:
            response = requests.get(url_with_cid, stream=True, timeout=30)
            response.raise_for_status()  # Raise exception if response status code is not 200
            file_path = config.DOWNLOAD_DIR+filename
            with open(file_path, 'wb') as f:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
            logging.info(":File downloaded successfully")
            return file_path
        except RequestException as e:
            logging.info(f"Error downloading from {url_with_cid}: {e}")

    logging.error("Could not download file from any of the URLs provided")
    return None


def get_now_datetime():
    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if __name__ == '__main__':
    print(search_net_book("平凡的世界", author="hhah" ,openid="openid"))

    # ipfs_id = 'bafykbzacedg535kz7z6imhntm5cuuknmutqmdktwt7di3l64cdi5vdepiohjk'
    # download_net_book(ipfs_id,"平凡的世界.epub")



