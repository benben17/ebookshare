import json
from datetime import datetime, timedelta
import logging
import threading
import requests
from sqlalchemy.exc import SQLAlchemyError

import config
from book import db, app
from book.dateUtil import dt_to_str, str_to_dt
from book.dicts import Product, PaymentStatus, UserRole
from book.models import UserPay, User
from book.utils import get_rss_host


def upgrade_user(user_name, days, pay_id, expires):
    path = '/api/v2/sync/user/upgrade'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user_name,
        'expiration_days': days,
        'expires': expires
    }
    try:
        res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS)
        if res.status_code == 200:
            data = json.loads(res.text)

            if data['status'].lower() == "ok":
                pay_log = UserPay.query.filter_by(id=pay_id).first()
                pay_log.status = PaymentStatus.completed
                pay_log.pay_time = str_to_dt(expires)
                db.session.add(pay_log)
                db.session.commit()
        logging.error("upgrade User error:%s".format(str(res.text)))
    except Exception as e:
        logging.error(str(e))


def upgrade_user_thread(user_name, p_name):
    try:
        p_dict = Product(p_name).get_product()
        p_days, p_desc = p_dict.get("days"), p_dict.get("desc")
        # 更新用户 为Plus用户
        user = User.query.filter_by(name=user_name).first()
        user.role = UserRole.role_name('plus')
        user.expires = datetime.now() + timedelta(days=p_days)
        db.session.add(user)

        user_pay = UserPay(user_id=user.id, user_name=user.name, currency='CNY', pay_type='ali',
                           product_name=p_name, description=p_desc, status=PaymentStatus.created)
        db.session.add(user_pay)
        db.session.commit()
        logging.info("开始升级用户-----")

        threading.Thread(target=upgrade_user, args=[user.name, p_days, user_pay.id]).start()
    except SQLAlchemyError as e:
        logging.error(e)
        db.session.rollback()
    except Exception as e:
        logging.error(e)


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
        print(json.loads(res.text))
        print("----------")
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
        pay_log = User.get_by_id(1681116305)
        print(pay_log.name)
        product = Product('month').get_product()
        print(datetime.now() + timedelta(days=3))