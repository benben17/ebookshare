import logging
from threading import Thread
from flask_mail import Message
from book import mail, app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, body, receiver, attach=None):
    msg = Message(subject, recipients=[receiver])
    if attach is not None:
        try:
            with open(attach, 'rb') as f:
                msg.attach(subject, 'application/octet-stream', f.read())
        except Exception as e:
            logging.error('open file failed.' + e)
    msg.html = body

    logging.info(f'发送邮件.{subject}-接收邮箱{receiver}')
    Thread(target=send_async_email, args=[app, msg]).start()
    return u'发送成功'
