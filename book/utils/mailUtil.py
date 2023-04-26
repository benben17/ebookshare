import logging
from threading import Thread
from flask_mail import Message
from book import mail, app
from book.utils.wxMsg import mail_body


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logging.error("send email failed")
            logging.error(str(e))


def send_email(subject, body, receiver, attach=None):
    msg = Message(subject, recipients=[receiver])
    if attach is not None:
        try:
            with open(attach, 'rb') as f:
                msg.attach(subject, 'application/octet-stream', f.read())
        except Exception as e:
            logging.error('open file failed.' + e)
    msg.html = body
    logging.info(f'send mail .subject: {subject}- receive:{receiver}')
    from book import app
    Thread(target=send_async_email, args=[app, msg]).start()
    return u'发送成功'



