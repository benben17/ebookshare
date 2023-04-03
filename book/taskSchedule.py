import datetime

from flask import logging
from flask_apscheduler import APScheduler

import config

scheduler = APScheduler()
import logging
from book.wxMsg import mail_body, send_failed_body, mail_url_body
from book import send_email, app, download_net_book, email_att_or_url


class Config(object):
    SCHEDULER_API_ENABLED = True

scheduler.init_app(app)
scheduler.start()

# interval example, 间隔执行, 每30秒执行一次
@scheduler.task('interval', id='book_send', seconds=180, misfire_grace_time=900, max_instances=3)
def bookSend():
    from book.dbModels import Userlog
    from book.dbModels import db
    # logging.info("start task....")
    with app.app_context():
        userlogs = Userlog.query.filter(Userlog.status == 0).all()
        if userlogs:
            for userlog in userlogs:
                file_path = download_net_book(userlog.ipfs_cid, userlog.book_name)
                print(file_path)
                if file_path:
                    try:
                        if email_att_or_url(file_path):
                            send_email(userlog.book_name, mail_body(userlog.book_name), userlog.receive_email,
                                       file_path)
                            userlog.status = config.SUCCESS_FLAG
                            userlog.create_time = datetime.datetime.now()
                            db.session.add(userlog)
                            db.session.commit()
                        else:
                            send_email(userlog.book_name, mail_url_body(), userlog.receive_email)
                        logging.info("发送成功"+userlog.book_name+userlog.receive_email)
                    except Exception as e:
                        logging.error(e)
                elif file_path is None:
                    send_email(userlog.book_name+"-发送失败", send_failed_body(userlog.book_name), userlog.receive_email)
                    userlog.status = config.FAILED_FlAG
                    db.session.add(userlog)
                    db.session.commit()
        # logging.info('无发送任务')



