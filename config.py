import os
APPID = "wx0630c28def50cbfd"
APPSECRET = "20764c0ae174a1e12c78e809a877c382"
wechat_token = "kindlebooks"

UPLOAD_FOLDER = "/var/www"

SECRET_KEY = os.getenv('SECRET_KEY','ebook')
SQLALCHEMY_DATABASE_URI = "sqlite:///ebook.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True