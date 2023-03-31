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
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
MAIL_USERNAME = 'librz.link@gmail.com'
MAIL_PASSWORD = 'hyqycxwwiwcwiswi'
MAIL_DEFAULT_SENDER = '"kindlebooks"<librz.link@gmail.com>'


CACHE_TYPE = "simple"

# 下面五个参数是所有的类型共有的
CACHE_NO_NULL_WARNING = "warning" # null类型时的警告消息
CACHE_ARGS = []    # 在缓存类实例化过程中解包和传递的可选列表，用来配置相关后端的额外的参数
CACHE_OPTIONS = {}    # 可选字典,在缓存类实例化期间传递，也是用来配置相关后端的额外的键值对参数
CACHE_DEFAULT_TIMEOUT = 600 # 默认过期/超时时间，单位为秒
CACHE_THRESHOLD = 100   # 缓存的最大条目数

BOOK_FILE_DIR = "/data/" # 电子书存放目录
