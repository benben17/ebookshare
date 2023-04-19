import json
from datetime import datetime, timedelta
import logging
import threading
import requests
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

import config
from book import db, app
from book.dateUtil import dt_to_str
from book.dicts import Product, PaymentStatus, UserRole
from book.models import UserPay, User
from book.utils import get_rss_host


def upgrade_user(user_name, days, expires, pay_id):
    data = {'key': config.RSS2EBOOK_KEY, 'user_name': user_name, 'expiration_days': days,
            'expires': dt_to_str(expires)
            }
    try:
        res = requests.post(get_rss_host() + '/api/v2/sync/user/upgrade', data=data, headers=config.HEADERS)
        if res.status_code == 200:
            data = json.loads(res.text)
            logging.info(data)
            if data['status'].lower() == "ok":
                with app.app_context():
                    pay_log = UserPay.query.filter_by(id=pay_id).first()
                    if days <= 0:  # 退款用户
                        logging.info("refund")
                        logging.info(pay_log.status)
                        pay_log.status = PaymentStatus.refund
                        pay_log.refund_time = datetime.now()
                        pay_log.refund_amount = pay_log.amount
                    else:
                        logging.info("charge")
                        pay_log.status = PaymentStatus.completed
                        pay_log.pay_time = datetime.now()
                    db.session.add(pay_log)
                    db.session.commit()
                    # print(pay_log.refund_time)
        logging.info("upgrade User success:{}".format(user_name))
    except Exception as e:
        logging.error("upgrade User:{} failed:{}".format(user_name, str(e)))


def upgrade_user_thread(type, user_name, p_name):
    try:
        user = User.query.filter(or_(User.name == user_name, User.email == user_name)).first()
        if not user:
            return False
        # 写入日志
        if type == 'upgrade':
            p_dict = Product(p_name).get_product()
            user_pay = UserPay(user_id=user.id, user_name=user.name, currency='CNY', pay_type='alipay',
                               amount=p_dict.get("cny"),
                               product_name=p_name, description=p_dict.get("desc"), status=PaymentStatus.created)
            db.session.add(user_pay)
            db.session.commit()
            days = int(p_dict.get("days"))
            logging.info("开始升级用户-----{}".format(user.name))
        else:
            user_pay = UserPay.query.filter(UserPay.status == PaymentStatus.completed,
                                            UserPay.user_name == user.name,
                                            UserPay.pay_type == 'alipay').order_by(UserPay.pay_time.desc()).first()
            if not user_pay:
                return False
            p_dict = Product(user_pay.product_name).get_product()  # 退款用户直接从付款表里面获取
            days = -int(p_dict.get("days"))
            logging.info("开始退款：-----{}".format(user.name))

        if user.expires:
            user.expires = user.expires + timedelta(days)
        else:
            user.expires = datetime.now() + timedelta(days)
        if user.expires > datetime.now():
            user.role = UserRole.role_name('plus')
        else:
            user.role = UserRole.role_name('default')
        db.session.add(user)
        db.session.commit()
        threading.Thread(target=upgrade_user, args=[user.name, days, user.expires, user_pay.id]).start()
        return True
    except SQLAlchemyError as e:
        logging.error(e)
        db.session.rollback()
        return False
    except Exception as e:
        logging.error(e)
        return False


def upgrade_user_by_paypal(user_name, days, expires):
    path = '/api/v2/sync/user/upgrade'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user_name,
        'expiration_days': days,
        'expires': dt_to_str(expires)
    }
    try:
        logging.info("google cloud update")
        logging.info(data)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        res = requests.post(get_rss_host() + path, data=data, headers=headers)
        # print(json.loads(res.text))
        # print("----------")
        if res.status_code == 200 and json.loads(res.text)['status'].lower() == 'ok':
            return True
    except requests.exceptions.RequestException as err:
        logging.error(err)
        return False
    except Exception as e:
        logging.error(e)
        return False


if __name__ == "__main__":
    with app.app_context():
        upgrade_user_thread('refund', 'admin', 'month')
    #     user_pay = UserPay.query.filter(UserPay.status == PaymentStatus.completed,
    #                                     UserPay.user_name == 'admin').order_by(UserPay.pay_time.desc()).first()
    #
    #     print(user_pay.id)
    # h = {"send_day": [11]}
    # product = Product('test').get_product()
    # print(product)
    # print(type(['type']))
    # r = h.get('send_day') if isinstance(h.get('send_day'), list) else ['Sunday']
    # print(r)
