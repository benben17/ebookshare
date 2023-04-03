import datetime
import os
import logging
from flask_apscheduler import APScheduler
import config
from book.wxMsg import mail_body, send_failed_body, mail_download_url_body
from book import send_email, app, download_net_book, email_att_or_url, get_file_suffix, allowed_ebook_ext
class Config(object):
    SCHEDULER_API_ENABLED = True
scheduler = APScheduler()


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
                        if email_att_or_url(file_path) is False:
                            send_email(userlog.book_name, mail_body(userlog.book_name), userlog.receive_email,
                                       file_path)
                        else:
                            send_email(userlog.book_name, mail_download_url_body(userlog.book_name), userlog.receive_email)

                        userlog.status = config.SUCCESS_FLAG
                        userlog.create_time = datetime.datetime.now()
                        db.session.add(userlog)
                        db.session.commit()
                        logging.info("发送成功"+userlog.book_name+userlog.receive_email)
                    except Exception as e:
                        logging.error(e)
                elif file_path is None:
                    send_email(userlog.book_name+"-发送失败", send_failed_body(userlog.book_name), userlog.receive_email)
                    userlog.status = config.FAILED_FlAG
                    db.session.add(userlog)
                    db.session.commit()
        # logging.info('无发送任务')

@scheduler.task('interval', id='delete_file', hours=1, misfire_grace_time=900)
def delete_file_out_24_hours():
    for filename in os.listdir(config.DOWNLOAD_DIR):
        file_path = os.path.join(config.DOWNLOAD_DIR, filename)
        suffix = get_file_suffix(file_path)
        # 判断是否为文件
        if os.path.isfile(file_path) and allowed_ebook_ext(suffix):
            # 获取文件创建时间
            create_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            # 计算时间差
            time_diff = datetime.datetime.now() - create_time
            # 如果时间差大于24小时，则删除文件
            if time_diff.total_seconds() > 24 * 60 * 60:
                os.remove(file_path)


