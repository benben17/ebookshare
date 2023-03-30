import json
import logging
from pathlib import Path
import requests
import yaml

class WeChat:
    def __init__(self):
        config = self.get_config('wechat')
        self.APPID = config['APPID']
        self.APPSECRET= config['APPSECRET']

    def get_config(self, param):
        BASE_DIR = Path(__file__).resolve().parent.parent
        with open(str(BASE_DIR) + '/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            return config[param]

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
    wechat = WeChat()
    wechat.get_token()