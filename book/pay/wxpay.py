import json
import string
import time
from base64 import b64encode
from random import random
from urllib.parse import urlparse

import requests
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

import config
from book.dicts import Product
from book.pay.common import get_order_no
from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/wxpay')


# paypalrestsdk.set_config(live_config)


@blueprint.route("/payment", methods=['GET', 'POST'])
@jwt_required()
def create_payment():
    wx = WXPay()
    notify_url = config.MY_DOMAIN + "/api/v2/wxpay/notify_url"
    data = request.get_json()
    product = data.get('product')
    if str(product).lower() not in ("month", "year", 'rss2ebook'):
        return APIResponse.bad_request(msg="Missing required product")

    p_dict = Product(str(product).lower()).get_product()
    p_name, p_amount, p_desc = p_dict['name'], p_dict['amount'], p_dict['desc']

    data = {
        "mchid": wx.mchid,
        "out_trade_no": get_order_no(),  # 订单号
        "appid": wx.appid,
        "description": p_desc,  # 商品描述
        "notify_url": wx.notify_url,
        "amount": {
            "total": p_amount,  # 总金额(分)
            "currency": "CNY"
        }
    }
    return wx.request(wx.payment_url, 'POST', data)


def refund(transaction_id, out_refund_no, refund, reason):
    wx = WXPay()
    data = {
            "transaction_id": transaction_id,  # 微信支付订单号(交易单号)
            "out_refund_no": out_refund_no,  # 商户退款单号(商户单号)
            "reason": reason,  # 退款原因
            "notify_url": wx.notify_url,  # 通知Url
            "amount": {
                "total": refund,  # 订单金额
                "refund": refund,  # 退款金额(分)
                "currency": "CNY"
            }
        }
    return wx.request(wx.refund_url, 'POST', data)


class WXPay:
    """ 微信 Native支付
    """

    def __init__(self):
        self.appid = "wx1fxxxxxc0eeexxx"  # APPID
        self.mchid = "100000001"  # 商户号
        self.payment_url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/native'  # Native支付下单接口
        self.refund_url = 'https://api.mch.weixin.qq.com/v3/refund/domestic/refunds'  # 退款接口
        self.notify_url = "https://weixin.qq.com/"  # 通知url
        self.serial_no = '48757XXXX9D9CD835841B45969B0XXXXXXXXXXXX'  # 商户证书序列号
        self.apiclient_key = './apiclient_key.pem'  # 本地证书路径

    # 生成签名
    # def get_sign(self, sign_str):
    #     rsa_key = RSA.importKey(open(self.apiclient_key).read())
    #     signer = pkcs1_15.new(rsa_key)
    #     digest = SHA256.new(sign_str.encode('utf8'))
    #     sign = b64encode(signer.sign(digest)).decode('utf-8')
    #     return sign

    def request(self, url: str, method: str, data: dict = None):
        data = json.dumps(data) if data else ''
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        timestamp = str(int(time.time()))
        sign_str = '\n'.join([
            method.upper(),  # HTTP请求方法
            url.split(urlparse(url).netloc)[-1],  # path+args
            timestamp,  # 时间戳
            random_str,  # 请求随机串
            data, ''  # 请求报文主体
        ])  # 结尾空窜仅用于让后面多一个\n
        sign = self.get_sign(sign_str)

        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json',
            'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mchid}",nonce_str="{random_str}",signature="{sign}",timestamp="{timestamp}",serial_no="{self.serial_no}"'
        }
        response = requests.request(url=url, method=method, data=data, headers=headers)
        return response

    def get_sign(self, sign_str):
        pass


