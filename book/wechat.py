import datetime
import json
import logging
import time
import requests
import yaml

import config


class WeChat:
    def __init__(self):
        self.APPID = config.APPID
        self.APPSECRET= config.APPSECRET

    def get_token(self):
        token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'
        try:
            res = requests.get(token_url.format(self.APPID,self.APPSECRET))
            json_res = json.loads(res.text)
            if 'access_token' in json_res:
                return json_res['access_token']
        except Exception as e:
            logging.error("获取token 失败！："+e)

if __name__ == '__main__':
    print(str(int(time.time())))