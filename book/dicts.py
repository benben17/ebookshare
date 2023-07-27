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
    refund = "refund"


class RequestStatus:
    OK = "ok"
    MSG = "msg"
    DATA = 'data'


class UserRole(Enum):
    DEFAULT = {"name": 'default', "feed_num": 10, 'interval': 20}
    PLUS = {"name": 'plus', "feed_num": 200, 'interval': 4}

    @staticmethod
    def get_role(role='default'):
        return UserRole[role.upper()].value if role.upper() in UserRole.__members__ else None

    @staticmethod
    def role_feed_num(role='default'):
        return UserRole[role.upper()].value.get('feed_num')

    @staticmethod
    def get_send_interval(role='default'):
        return UserRole[role.upper()].value.get('interval')

    @staticmethod
    def role_name(role='default'):
        return UserRole[role.upper()].value.get('name', 'default')


class Product:
    products = {
        "month": {"name": "month", "amount": 2.9, "desc": "rss2Ebook One month plus fee", "days": 31, 'cny': 15},
        "year": {"name": "year", "amount": 24.9, "desc": "rss2Ebook One year plus fee", "days": 366, "cny": 99},
        "rss2ebook": {"name": "rss2ebook", "amount": 0.9, "desc": "rss2Ebook for test", "days": 20, 'cny': 1}
    }

    def __init__(self, product=None):
        self.product = str(product).lower() if str(product).lower() else 'rss2ebook'

    def get_product(self):
        return Product.products.get(self.product) if Product.products.get(self.product) else Product.products.get("rss2ebook")


if __name__ == "__main__":
    days = -10
    print(UserRole.get_role())
    # print(datetime.utcnow() + timedelta(days=int(days)))
    # day = 'Sunday'
    # p_dict = Product("hahha").get_product()
    # user = {"role": None}
    # user_role = user['role'] if user['role'] else 'default'
    # print(UserRole.get_send_interval(user_role))
