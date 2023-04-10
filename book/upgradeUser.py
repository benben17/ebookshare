import json
from datetime import datetime, timedelta
import logging
import threading
import requests
from flask_sqlalchemy.session import Session

import config
from book import db, app
from book.models import UserPay


def upgrade_user(user_name, days, expires, pay_id):
    path = '/api/v2/sync/user/upgrade'
    data = {
        'key': config.RSS2EBOOK_KEY,
        'user_name': user_name,
        'expiration_days': days,
        'expires': expires
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(config.RSS2EBOOK_URL + path, data=data, headers=headers)
    if res.status_code != 200:
        logging.error(res.text)
    if res.status_code == 200:
        try:
            data = json.loads(res.text)
            pay_log = UserPay.query.filter_by(id=pay_id).first()
            if data['status'].lower() == "ok":
                pay_log.status = 1
            else:
                pay_log.status = 0
            db.session.add(pay_log)
            db.session.commit()
        except Exception as e:
            logging.error(str(e))






def upgrade_user_thread(user, days):
    user.role = 'plus'
    user.expires = datetime.utcnow() + timedelta(days=days+1)
    db.session.add(user)
    db.session.commit()


    p_name = "月卡"
    if int(days) > 180:
        p_name = "年卡"
    pay_log = UserPay(user_id=user.id, user_email=user.email, pay_type='ali', name = p_name)
    db.session.add(pay_log)
    db.session.commit()

    logging.info("开始升级用户")
    threading.Thread(target=upgrade_user, args=[user.name, days, user.expires, pay_log.id]).start()


if __name__ == "__main__":
    with app.app_context():
        pay_log = UserPay.query.filter_by(id=1).first()