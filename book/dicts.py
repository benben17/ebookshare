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
    approved = "approved"
    completed = "completed"
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
    def __init__(self, product):
        self.product = product

    def get_product(self):
        if self.product == "month":
            return {"name": "month", "amount": 2.99, "desc": "One month plus fee", "days": 31}
        elif self.product == "year":
            return {"name": "year", "amount": 19.99, "desc": "One year plus fee", "days": 366}
        else:
            return {"name": "test", "amount": 0.01, "desc": "for test", "days": 10}


if __name__ == "__main__":
    days = -10
    print(datetime.utcnow() + timedelta(days=int(days)))
    day = 'Sunday'
    print(day.split("|"))
    print(UserRole.role_name())
