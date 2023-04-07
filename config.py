import os
from datetime import timedelta

basedir= os.path.abspath(os.path.dirname(__file__))
APPID = "wx0630c28def50cbfd"
APPSECRET = "20764c0ae174a1e12c78e809a877c382"
wechat_token = "kindlebooks"

SECRET_KEY = os.getenv('SECRET_KEY','ebook')

SQLALCHEMY_DATABASE_URI = "sqlite:///"+ os.path.join(basedir,'db/ebook.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True

os.environ['TZ']= 'Asia/Shanghai'

# flask mail
# Flask-Mail settings
MAIL_ON_OFF = 'ON'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
MAIL_USERNAME = 'librz.link@gmail.com'
MAIL_PASSWORD = 'hyqycxwwiwcwiswi'
MAIL_DEFAULT_SENDER = '"ebookshare"<librz.link@gmail.com>'
MAIL_ATT_MAX_SIZE = 20   # 设置附件大小 单位M

CACHE_TYPE = "simple"

# 下面五个参数是所有的类型共有的
CACHE_NO_NULL_WARNING = "warning" # null类型时的警告消息
CACHE_ARGS = []    # 在缓存类实例化过程中解包和传递的可选列表，用来配置相关后端的额外的参数
CACHE_OPTIONS = {}    # 可选字典,在缓存类实例化期间传递，也是用来配置相关后端的额外的键值对参数
CACHE_DEFAULT_TIMEOUT = 600  # 默认过期/超时时间，单位为秒
CACHE_THRESHOLD = 100   # 缓存的最大条目数

JSON_AS_ASCII = False

#JWT
JWT_SECRET_KEY = 'rss2ebook'
JWT_ACCESS_TOKEN_EXPIRES = False
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

SCHEDULER_TIMEZONE = 'Asia/Shanghai'  # 配置时区
SCHEDULER_API_ENABLED = True  # 添加API

# 电子书下载目录
DOWNLOAD_DIR = os.path.join(basedir, 'ebooks/')
# print(DOWNLOAD_DIR)
DOWNLOAD_URL = "https://ebook.stararea.cn/download/"
# 发送邮件状态
SEND_FAILED = 3   # 失败
SEND_SUCCESS = 1   # 成功
SEND_UNKONOW = 4

PAGE_NUM = 10 #每页显示条数

RSS2EBOOK_URL = 'https://benben5-191802.an.r.appspot.com'
RSS2EBOOK_KEY = 'rss2Ebook.com.luck!'

DEFAULT_USER_ROLE = 'default'
DEFAULT_USER_PASSWD = 'sendtokindles'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}



