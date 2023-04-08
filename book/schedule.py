from flask_apscheduler import APScheduler
from flask_apscheduler.scheduler import BackgroundScheduler
from book.utils.wxMsg import mail_body, send_failed_body, mail_download_url_body
from book import app
from book.utils.mailUtil import send_email
from book.utils import *


def delete_file_out_24_hours():
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
    from book.dbModels import Userlog
    from book.dbModels import db

    with app.app_context():
        userlogs = Userlog.query.filter(Userlog.status == send_status).all()
        if userlogs:
            for userlog in userlogs:
                file_path = download_net_book(userlog.ipfs_cid, userlog.book_name)
                print(file_path)
                if file_path:
                    try:
                        if email_att_or_url(file_path) is False:
                            send_email(userlog.book_name, mail_body(userlog.book_name), userlog.receive_email,
                                       file_path)
                        else:
                            send_email(userlog.book_name, mail_download_url_body(userlog.book_name),
                                       userlog.receive_email)

                        userlog.status = config.SEND_SUCCESS

                        userlog.create_time = datetime.now()
                        db.session.add(userlog)
                        db.session.commit()
                        logging.info("发送成功" + userlog.book_name + userlog.receive_email)
                    except Exception as e:
                        logging.error(e)
                elif file_path is None:
                    send_email(userlog.book_name + "-下载文件失败", send_failed_body(userlog.book_name),
                               userlog.receive_email)
                    if int(send_status) == 4:
                        userlog.status = config.SEND_FAILED
                    else:
                        userlog.status = config.SEND_UNKONOW
                    db.session.add(userlog)
                    db.session.commit()


scheduler = APScheduler(BackgroundScheduler())
scheduler.init_app(app)

scheduler.add_job(id="delete_file", func=delete_file_out_24_hours, trigger="interval", hours=2, replace_existing=False)
scheduler.add_job(id="send_file", func=book_send, args=("0"), trigger="interval", seconds=180, replace_existing=False,
                  max_instances=3)
scheduler.add_job(id="retry_send_file", func=book_send, args=("4"), trigger="cron", day="*", hour="01",
                  replace_existing=False)
scheduler.start()




