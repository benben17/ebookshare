# coding: utf-8
from book import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    role = db.Column(db.String(120))
    srole = db.Column(db.Integer, default=0)
    hash_pass = db.Column(db.String(240))
    kindle_email = db.Column(db.String(120))
    wx_openid = db.Column(db.String(64), unique=True)
    upload_times = db.Column(db.Integer, default=0)
    download_times = db.Column(db.Integer, default=0)
    feed_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Integer, default=0)
    expires = db.Column(db.DateTime)  # 超过了此日期后账号自动停止推送
    create_time = db.Column(db.DateTime, default=datetime.now())
    is_reg_rss = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.name)


class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    author = db.Column(db.String(128))
    publisher = db.Column(db.String(128))
    extension = db.Column(db.String(128))
    filesize = db.Column(db.String(64))
    language = db.Column(db.String(24))
    publish_year = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    isbn = db.Column(db.String(30))
    tags = db.Column(db.String(128))
    db.UniqueConstraint('title', 'extension', name='idx_col1_col2')
    bookext = db.relationship('Bookurl', backref=db.backref('books'), uselist=False)


class Bookurl(db.Model):
    __tablename__ = "book_url"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book_download_url = db.Column(db.String(512))


class Userlog(db.Model):
    __tablename__ = "user_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_name = db.Column(db.String(300))
    operation_type = db.Column(db.String(24), default='download')
    receive_email = db.Column(db.String(120))
    download_time = db.Column(db.DateTime, default=datetime.now())
    create_time = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer)
    ipfs_cid = db.Column(db.String(300))
    filesize = db.Column(db.Integer)
    wx_openid = db.Column(db.String(120))


class UserPay(db.Model):
    __tablename__ = "user_pay"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(300))  # 年费 月费
    pay_type = db.Column(db.String(24))  # ali weixin
    user_email = db.Column(db.String(120))
    pay_time = db.Column(db.DateTime, default=datetime.now())
    create_time = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer)

    def __repr__(self):
        return self.user_name
