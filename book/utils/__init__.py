# -*-coding: utf-8-*-
import logging
import os.path
import re
import time, os
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import random
import requests
from requests.exceptions import RequestException
from sqlalchemy import inspect
from enum import Enum
import config
from book.utils.date_util import utc_to_local, get_now


def gen_userid():
    ymd = int(time.time())
    random_num = random.randint(100, 999)
    return int(f'{ymd}{random_num}')


def parse_xml(xml_str):
    """解析xml字符串"""
    root = ET.fromstring(xml_str)
    msg_type = root.findtext('MsgType')
    from_user = root.findtext('FromUserName')
    to_user = root.findtext('ToUserName')
    content = root.findtext('Content')
    event = root.findtext('Event')
    return msg_type, from_user, to_user, content, event


def is_isbn(isbn):
    # ISBN 的长度为10或13
    if len(isbn) not in [10, 13]:
        return False
    if len(isbn) == 10:
        if not isbn[:-1].isdigit():
            return False
        groups = [int(d) for d in isbn]
        checksum = sum((i + 1) * x for i, x in enumerate(groups[:-1])) % 11
        if checksum == 10 and isbn[-1] not in ['X', 'x']:
            return False
        if checksum != 10 and str(checksum) != isbn[-1]:
            return False
    # 13位ISBN必须由数字和短横线组成
    if len(isbn) == 13:
        if not isbn.isdigit():
            return False
        groups = [int(d) for d in isbn]
        checksum = (10 - (sum(groups[::2]) + sum(groups[1::2]) * 3) % 10) % 10
        if str(checksum) != str(isbn[-1]):
            return False
    return True


def allowed_ebook_ext(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'mobi', 'azw3', 'epub'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_name(file):
    file_suffix = str(Path(file).suffix)
    return os.path.basename(file).replace(file_suffix, "")


def email_att_or_url(file):
    filesize = os.path.getsize(file)
    return filesize <= config.MAIL_ATT_MAX_SIZE


def get_file_suffix(file):
    if isinstance(file, str) and '.' in file:
        _, suffix = file.rsplit('.', 1)
        return suffix.lower()
    return None


def filesize_format(value, binary=False):
    """bugfix for do_filesizeformat of jinja2"""
    bytes = float(value)
    base = 1024 if binary else 1000
    prefixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    for i, prefix in enumerate(prefixes):
        unit = base ** i
        if bytes < base ** (i + 1):
            return f"{int(bytes / unit)}{prefix}"
    return f"{int(bytes / unit)}{prefixes[-1]}"


def net_book_content(books, from_user):
    if len(books) == 0:
        msg_content = f'你搜的书不存在，请尝试搜索其他书籍！\n'
        return msg_content, None
    book_count = len(books)
    msg_content = f'一共搜索到{book_count}本书:\n'
    msg_content_separator = '--------------------------\n'
    email_instructions = '回复【1-15】编号，发送到绑定邮箱\n'
    books_cache = {}

    for index, book in enumerate(books, start=1):
        author = str(book['author']).translate(str.maketrans('', '', '[]未知COAY.COMchenjin5.comePUBw.COM'))
        title = book['title'][:30]
        ext = book['extension']
        ipfs_cid = book['ipfs_cid']
        filesize = filesize_format(book['filesize'])
        filename = f'{title}.{ext}'
        msg_content += f'{index} :【{filename}】-{author}-{filesize}\n'
        books_cache[f'{from_user}_{index}'] = f'{filename}:{ipfs_cid}:{book["filesize"]}'

    msg_content += msg_content_separator + email_instructions
    return msg_content, books_cache


def cache_book(books, wx_openid):
    if len(books) == 0:
        return True
    books_cache = {}
    try:
        for index, book in enumerate(books, start=1):
            author = str(book['author']).translate(str.maketrans('', '', '[]未知COAY.COMchenjin5.comePUBw.COM'))
            title = book['title']
            title = title[:30]
            ext = book['extension']
            ipfs_cid = book['ipfs_cid']
            filesize = filesize_format(book['filesize'])
            filename = f'{title}.{ext}'
            books_cache[f'{wx_openid}_{index}'] = f'{filename}:{ipfs_cid}:{book["filesize"]}:{author}:{filesize}'
        from book import cache
        cache.set_many(books_cache)
        return True
    except Exception as e:
        logging.error(f"缓存错误:{e}")
        return False


def search_net_book(title=None, author=None, isbn=None, openid="", ):
    search_url = f'{config.BOOKSEARCH_URL}/search?limit=15&query='
    # print(search_url)
    if not any((title, author, isbn)):
        return None
    param = ''
    if title is not None:
        param += f'title:"{title}"'
    if author is not None:
        param += f'author:"{author}"'
    if isbn is not None:
        param += f'isbn:"{isbn}"'
    res = requests.get(url=search_url + param, timeout=30)
    if int(res.status_code) == 200:
        json_res = res.json()
        return net_book_content(json_res['books'], openid)
    return False


def download_net_book(ipfs_cid, filename):
    file_path = config.DOWNLOAD_DIR + filename

    # 当文件存在，不下载直接返回文件路径
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    url_list = [
        'https://dweb.link',
        'https://cloudflare-ipfs.com',
        'https://gateway.pinata.cloud',
        'https://gateway.ipfs.io',
        'https://ipfs.joaoleitao.org',
        'https://cf-ipfs.com',
        'https://hardbin.com'
    ]
    # file_download_url = 'https://netfile.rss2ebook.com'
    for url in url_list:
        full_url = f"{url}/ipfs/{ipfs_cid}?filename={filename}"
        for attempt in range(3):
            try:
                response = requests.get(full_url, stream=True, timeout=30)
                response.raise_for_status()  # Raise exception if response status code is not 200

                with open(file_path, 'wb') as f:
                    for data in response.iter_content(chunk_size=2048):
                        f.write(data)
                logging.info(f"{filename}:File downloaded successfully")
                return file_path
            except RequestException as e:
                logging.error(f"Error downloading from {full_url} on attempt {attempt + 1}: {e}")
                if attempt == 2:  # If this was the last attempt
                    return None
                time.sleep(5)
                # logging.error(f"{filename} Could not download file from any of the URLs provided")
        # return None


def is_file_24_hours(file_path):
    '''判断文件是否创建超过24小时'''
    ctime = os.path.getctime(file_path)
    current_time = time.time()
    return current_time - ctime > 24 * 60 * 60


def get_ymd_dt():
    return datetime.utcnow().strftime('%Y-%m-%d 00:00:00')


def new_secret_key(length=8):
    import random
    allchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY0123456789'
    return ''.join([random.choice(allchars) for i in range(length)])


def model_to_dict(model, tz=0):
    """
    Convert a SQLAlchemy model instance into a JSON-serializable dict.
    """
    if not model:
        return None
    # get the attributes of the model instance
    attributes = inspect(model).attrs
    filter_list = ["user_pay_log", "hash_pass", "user"]
    data = {}
    for attribute in attributes:
        if attribute.key in filter_list:
            continue
        value = getattr(model, attribute.key)
        # convert datetime objects to ISO format
        if isinstance(value, datetime):
            value = utc_to_local(value, tz=tz) if value is not None else None
        elif isinstance(value, Enum):
            value = value.value
        data[attribute.key] = value
    return data


def check_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.findall(pattern, email):
        return True
    else:
        return False


def generate_code():
    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    return ''.join(code)


def create_app_dir():
    dirs = ['logs', 'ebooks', 'db']
    for dir in dirs:
        # print(os.path.join(config.basedir, dir))
        if not os.path.exists(os.path.join(config.basedir, dir)):
            os.mkdir(os.path.join(config.basedir, dir))


def get_rss_host(user_id=1):
    if user_id % 2 == 1:
        return config.rss_host['primary']
    else:
        return config.rss_host['second']


def utc_now():
    return datetime.utcnow()


if __name__ == '__main__':
    # print(is_isbn('1-63995-000-1'))
    # print(get_now())
    # author = "[]未知12213COMchenjin5.comePUBw.COM 12344"
    # author = str(author).translate(str.maketrans('', '', '[]未知COAY.COMchenjin5.comePUBw.COM'))
    # print(author)
    # print(filesize_format(100022000000000000000000000000))
    # print(search_net_book("javascrip"))
    ipfs_id = 'bafykbzacedg535kz7z6imhntm5cuuknmutqmdktwt7di3l64cdi5vdepiohjk'
    download_net_book(ipfs_id,"平凡的世界.epub")
