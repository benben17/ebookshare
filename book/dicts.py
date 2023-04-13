# coding: utf-8
from datetime import datetime, timedelta
from enum import Enum


# 发送邮件状态

class SEND_STATUS:
    WAITING = 0  # 等待发送
    SUCCESS = 1  # 成功
    FAILED = 3  # 失败
    UNKONOW = 4  # 晚上重新发送一次


class PaymentStatus(Enum):
    created = "created"
    pending = "pending"
    approved = "approved"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class RequestStatus:
    OK = "ok"
    MSG = "msg"
    DATA = 'data'


class UserRole(Enum):
    DEFAULT = {"name": 'default', "feed_num": 5}
    PLUS = {"name": 'plus', "feed_num": 100}

    @staticmethod
    def get_role(role='default'):
        return UserRole[role.upper()].value if role.upper() in UserRole.__members__ else None

    @staticmethod
    def role_feed_num(role='default'):
        return UserRole[role.upper()].value.get('feed_num', 0)

    @staticmethod
    def role_name(role='default'):
        return UserRole[role.upper()].value.get('name', 'default')


class Product:
    products = {
        "month": {"name": "month", "amount": 2.9, "desc": "rss2Ebook One month plus fee", "days": 31, 'cny': 20},
        "year": {"name": "year", "amount": 19.9, "desc": "rss2Ebook One year plus fee", "days": 366, "cny": 99},
        "rss2ebook": {"name": "rss2ebook", "amount": 0.01, "desc": "rss2Ebook for test", "days": 2,'cny':1}
    }

    def __init__(self, product=None):
        self.product = str(product).lower() if str(product).lower() else 'test'

    def get_product(self):
        return Product.products.get(self.product, {"name": "test", "amount": 0.01, "desc": "for test", "days": 10})


if __name__ == "__main__":
    days = -10
    print(datetime.utcnow() + timedelta(days=int(days)))
    day = 'Sunday'
    p_dict = Product().get_product()
    print(p_dict)
