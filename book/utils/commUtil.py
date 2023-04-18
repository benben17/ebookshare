# -*-coding: utf-8-*-
import requests
import config,logging,json
from book.dicts import RequestStatus
from book.utils import get_rss_host
from book.utils.ApiResponse import APIResponse


def sync_post(path, param, user):
    """远程服务器请求方法"""
    if param:
        param['key'] = config.RSS2EBOOK_KEY
        param['user_name'] = user['name']
        param['creator'] = user['name']
        #get_rss_host()
    res = requests.post('http://127.0.0.1:8080' + path, data=param, headers=config.HEADERS, timeout=60)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        if json_data['status'] == RequestStatus.OK:
            if RequestStatus.DATA not in json_data.keys():
                json_data['data'] = ""
            return json_data
        return {"status": "failed", "msg": json_data[RequestStatus.MSG]}
    else:
        logging.error(str(path), res.text)
        return {"status": "failed", "msg": res.text}


def return_fun(res):
    if res['status'].lower() == RequestStatus.OK:
        return APIResponse.success(msg=res[RequestStatus.MSG], data=res[RequestStatus.DATA])
    else:
        return APIResponse.bad_request(msg=res[RequestStatus.MSG])
