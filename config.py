import os
APPID = "wx0630c28def50cbfd"
APPSECRET = "20764c0ae174a1e12c78e809a877c382"
wechat_token = "kindlebooks"

UPLOAD_FOLDER = "/var/www"

SECRET_KEY = os.getenv('SECRET_KEY','ebook')
SQLALCHEMY_DATABASE_URI = "sqlite:///ebook.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True


# flask mail
# Flask-Mail settings
MAIL_ON_OFF = 'ON'
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'cljqqyx@qq.com'
MAIL_PASSWORD = 'xxx'
MAIL_DEFAULT_SENDER = '"test"<cljqqyx@qq.com>'
