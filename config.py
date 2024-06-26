import os
from datetime import timedelta

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
DEBUG = os.getenv('DEBUG', False)
APPID = os.getenv("APPID")
APPSECRET = os.getenv("APPSECRET")
wechat_token = os.getenv("WECHATTOKEN")



# sqllite
SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'db/ebook.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
CSRF_ENABLED = True

os.environ['TZ'] = 'Asia/Shanghai'

# Flask-Mail settings
MAIL_ON_OFF = 'ON'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_DEBUG = False
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
MAIL_ATT_MAX_SIZE = 20  # 设置附件大小 单位M

# 下面五个参数是所有的类型共有的
CACHE_TYPE = "simple"
CACHE_NO_NULL_WARNING = "warning"  # null类型时的警告消息
CACHE_ARGS = []  # 在缓存类实例化过程中解包和传递的可选列表，用来配置相关后端的额外的参数
CACHE_OPTIONS = {}  # 可选字典,在缓存类实例化期间传递，也是用来配置相关后端的额外的键值对参数
CACHE_DEFAULT_TIMEOUT = 600  # 默认过期/超时时间，单位为秒
CACHE_IGNORE_ERRORS = True
CACHE_THRESHOLD = 10000  # 缓存的最大条目数

JSON_AS_ASCII = False

# JWT
JWT_SECRET_KEY = 'rss2ebook'
JWT_ACCESS_TOKEN_EXPIRES = False
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

SCHEDULER_TIMEZONE = 'Asia/Shanghai'  # 配置时区
SCHEDULER_API_ENABLED = False  # 添加API

MY_DOMAIN = 'https://rss2ebook.com/prod-api'
# 电子书 配置
DOWNLOAD_DIR = os.path.join(basedir, 'ebooks/')   # 下载目录
DOWNLOAD_URL = MY_DOMAIN+"/download/"  # 下载URL
BOOKSEARCH_URL = "https://zlib.knat.network"        # ebook 搜索地址
rss_host = {    # rss 源后台主机
    "primary": "https://benben5-191802.an.r.appspot.com",
    "second": "https://benben10-191802.an.r.appspot.com"
}


RSS2EBOOK_KEY = os.getenv('RSS2EBOOK_KEY')
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


# 在Google Cloud Platform 中创建 OAuth 2.0 客户端 ID 时指定的值
OAUTH_CREDENTIALS = {
    'google': {
        'id': os.getenv('GOOGLE_ID'),
        'secret': os.getenv('GOOGLE_SECRET')
    }
}

UPGRADE_USER_URL = "https://rss2ebook.com/user/upgrade"
