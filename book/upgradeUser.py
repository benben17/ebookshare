import datetime
import logging
import threading

import requests

import config
from book import db


def upgrade_user(user_name,days):
    path = '/api/v2/sync/user/upgrade'
    data = {}
    data['key'] = config.RSS2EBOOK_KEY
    data['user_name'] = user_name
    data['days'] = days
    res = requests.post(config.RSS2EBOOK_URL + path, data=data, headers=config.headers)
    if res.status_code != 200:
        logging.error(res.text)


def upgrade_user_thread(user, days):
    user.role = 'vip'
    user.expires = datetime.datetime.utcnow() + datetime.timedelta(days=days+1)
    db.session.add(user)
    db.session.commit()
    t = threading.Thread(target=upgrade_user, args=[user.name, days])
    t.start()
    logging.info("开始升级用户")