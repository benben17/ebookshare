# -*-coding: utf-8-*-

import random
import requests
import config, logging, json
from book.dicts import RequestStatus
from book.utils import get_rss_host
from book.utils.ApiResponse import APIResponse


def sync_post(path, param, user=None):
    """远程服务器请求方法"""

    if user is None:
        param = {}
    else:
        param['user_name'] = user['name']
        param['creator'] = user['name']
    param['key'] = config.RSS2EBOOK_KEY

    request_host = get_rss_host()
    # request_host = 'http://127.0.0.1:8080'
    try:
        res = requests.post(request_host + path, data=param, headers=config.HEADERS, timeout=60)
        if res.status_code == 200:
            json_data = json.loads(res.text)
            if json_data['status'] == RequestStatus.OK:
                if RequestStatus.DATA not in json_data.keys():
                    json_data['data'] = ""
                return json_data
            return {"status": "failed", "msg": json_data[RequestStatus.MSG]}
        else:
            logging.error(res.text)
            return {"status": "failed", "msg": res.text}
    except Exception as e:
        return {"status": "failed", "msg": "system error"}


def return_fun(res):
    if res['status'].lower() == RequestStatus.OK:
        return APIResponse.success(msg=res[RequestStatus.MSG], data=res[RequestStatus.DATA])
    else:
        return APIResponse.bad_request(msg=res[RequestStatus.MSG])


def sync_user(user):
    path = '/api/v2/sync/user/add'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user.name,
        'to_email': user.email
    }
    res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS)
    if res.status_code == 200:
        res = json.loads(res.text)
        if res['status'].lower() == RequestStatus.OK:
            return True
    return False


def new_passwd():
    randomStr = ""
    for i in range(8):
        temp = random.randrange(0, 3)
        if temp == 0:
            ch = chr(random.randrange(ord('A'), ord('Z') + 1))
            randomStr += ch
        elif temp == 1:
            ch = chr(random.randrange(ord('a'), ord('z') + 1))
            randomStr += ch
        else:
            ch = str((random.randrange(0, 10)))
            randomStr += ch

    return randomStr


class CacheKey:

    mybook = 'books:{}'
    resetKey = 'passwd_reset:{}'
    sendCount = 'email_send_count:{}'
    pub_rss_key = 'pub_rss_key'
    deliverKey = 'deliver:{}'
    rss_user_info = 'user_info:{}'
    my_rss = 'my_rss:{}'




