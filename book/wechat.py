import datetime
import json
import logging
import time
import requests
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
                # cache.add('access_token',json_res['access_token'])
                return json_res['access_token']
        except Exception as e:
            logging.error("获取token 失败！："+e)
    def create_menu(self):
        ACCESS_TOKEN = self.get_token()
        create_menu_button_url= f'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={ACCESS_TOKEN}'
        my = "http://www.baidu.com"
        param = '''{
            "button": [
                {
                    "type": "click",
                    "name": "个人中心",
                    "key": "{my}"
                },
                {
                    "name": "菜单",
                    "sub_button": [
                        {
                            "type": "view",
                            "name": "搜索",
                            "url": "http://www.soso.com/"
                        },
                        {
                            "type": "click",
                            "name": "赞一下我们",
                            "key": "V1001_GOOD"
                        }]
                }]
        }'''
        param.format(my)
        requests.post(create_menu_button_url,param)

        try:
            print("a")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    print(str(int(time.time())))