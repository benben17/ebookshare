# encoding:utf-8
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from book.dicts import SEND_STATUS
from book.utils import *
from book.utils.mailUtil import send_email
from book.utils.wxMsg import mail_body, send_failed_body, mail_download_url_body


def del_file_out_24h():
    """
    删除24小时之前的文件
    :return:
    """
    logging.info("delete_file_out_24_hours")
    for filename in os.listdir(config.DOWNLOAD_DIR):
        file_path = os.path.join(config.DOWNLOAD_DIR, filename)
        # 判断是否为文件
        if os.path.isfile(file_path) and allowed_ebook_ext(os.path.basename(file_path)):
            # 获取文件创建时间
            create_time = datetime.fromtimestamp(os.path.getctime(file_path))
            # 计算时间差
            time_diff = datetime.now() - create_time
            # 如果时间差大于24小时，则删除文件
            if time_diff.total_seconds() > 24 * 60 * 60:
                os.remove(file_path)
                logging.info(f"delete file : {file_path}")


def book_send(send_status):
    from book.models import Userlog, db
    from book import app
    with app.app_context():
        userlogs = Userlog.query.filter(Userlog.status == send_status).all()
        if not userlogs:  # 无数据直接返回
            return ""
        for userlog in userlogs:
            file_path = download_net_book(userlog.ipfs_cid, userlog.book_name)
            if file_path:
                try:
                    if email_att_or_url(file_path) is False:
                        send_email(userlog.book_name, mail_body(userlog.book_name), userlog.receive_email,
                                   file_path)
                    else:
                        send_email(userlog.book_name, mail_download_url_body(userlog.book_name),
                                   userlog.receive_email)

                    userlog.status = SEND_STATUS.SUCCESS.value
                    userlog.create_time = datetime.now()
                    db.session.add(userlog)
                    db.session.commit()
                    logging.info("发送成功" + userlog.book_name + userlog.receive_email)
                except Exception as e:
                    logging.error(e)
            elif file_path is None:
                send_email(userlog.book_name + "-下载文件失败", send_failed_body(userlog.book_name),
                           userlog.receive_email)
                if int(send_status) == SEND_STATUS.UNKNOWN.value:
                    userlog.status = SEND_STATUS.FAILED.value
                else:
                    userlog.status = SEND_STATUS.UNKNOWN.value
                db.session.add(userlog)
                db.session.commit()


def init_scheduler(appName):
    executors = {
        'default': ThreadPoolExecutor(10),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': True,
        'max_instances': 3
    }
    scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

    scheduler.add_job(id="delete_file", func=del_file_out_24h, trigger="cron", day="*", hour='02',
                      replace_existing=False)
    scheduler.add_job(id="send_file", func=book_send, args=(str(SEND_STATUS.WAITING.value),), trigger="interval", seconds=180,
                      replace_existing=False, max_instances=3)
    scheduler.add_job(id="retry_send_file", func=book_send, args=(str(SEND_STATUS.UNKNOWN.value),), trigger="cron", day="*",
                      hour="01",
                      replace_existing=False)

    flask_scheduler = APScheduler(scheduler)
    flask_scheduler.init_app(appName)
    flask_scheduler.start()
