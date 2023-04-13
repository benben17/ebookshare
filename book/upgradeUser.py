import json
from datetime import datetime, timedelta
import logging
import threading
import requests
from flask_sqlalchemy.session import Session
from sqlalchemy.exc import SQLAlchemyError

import config
from book import db, app
from book.dateUtil import get_days_later, dt_to_str, str_to_dt
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
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(get_rss_host() + path, data=data, headers=headers)
    if res.status_code != 200:
        logging.error(res.text)
    if res.status_code == 200:
        try:
            data = json.loads(res.text)
            pay_log = UserPay.query.filter_by(id=pay_id).first()
            if data['status'].lower() == "ok":
                pay_log.status = PaymentStatus.completed
            else:
                pay_log.status = PaymentStatus.created
            pay_log.pay_time = str_to_dt(expires)
            db.session.add(pay_log)
            db.session.commit()
        except Exception as e:
            logging.error(str(e))


def upgrade_user_thread(user, days):
    try:
        user.role = UserRole.role_name('plus')
        user.expires = datetime.utcnow() + timedelta(days=days)
        db.session.add(user)
        p_name = "month"
        if int(days) > 180:
            p_name = "year"
        pay_log = UserPay(user_id=user.id, user_email=user.email, pay_type='ali', name=p_name)
        db.session.add(pay_log)
        db.session.commit()

        logging.info("开始升级用户-----")
        threading.Thread(target=upgrade_user, args=[user.name, days, pay_log.id]).start()
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
