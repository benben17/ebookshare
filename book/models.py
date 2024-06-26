# coding: utf-8
from sqlalchemy import Enum

from book import db, dicts, cache
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
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
    timezone = db.Column(db.Integer, default=0)
    is_reg_rss = db.Column(db.Boolean, default=False)
    user_pay_log = db.relationship(
        "UserPay", uselist=True, backref="user", lazy='dynamic')

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

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_tz(cls, id):
        tz_key = str(id)+'timezone'
        tz = cache.get(tz_key)
        if tz is not None:
            return int(tz)
        u = cls.get_by_id(id)
        cache.set(tz_key, u.timezone if u else 0)
        return u.timezone if u else 0

    @classmethod
    def get_feed_count(cls, id):
        return cls.get_by_id(id).feed_count if cls.get_by_id(id) else 0

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


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
    bookext = db.relationship(
        'Bookurl', backref=db.backref('books'), uselist=False)


class Bookurl(db.Model):
    __tablename__ = "book_url"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book_download_url = db.Column(db.String(512))


class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
    id = db.Column(db.Integer, primary_key=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    product_name = db.Column(db.String(100))  # 年费 月费
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pay_type = db.Column(db.String(24))  # ali weixin
    user_name = db.Column(db.String(120))
    pay_time = db.Column(db.DateTime)
    pay_url = db.Column(db.String(500))  # 支付地址，未支付的时候直接调用
    create_time = db.Column(db.DateTime, default=datetime.utcnow())
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(Enum(dicts.PaymentStatus),
                       default=dicts.PaymentStatus.created)
    payment_id = db.Column(db.String(255), nullable=True, index=True)
    cancel_url = db.Column(db.String(255), nullable=True)
    canceled_by = db.Column(db.String(255), nullable=True)
    canceled_time = db.Column(db.DateTime, nullable=True)
    refund_time = db.Column(db.DateTime, nullable=True)
    refund_amount = db.Column(db.Float, nullable=True, default='0.00')

    # refund_read_amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return self.user_name

    @classmethod
    def get_payment_id(cls, payment_id):
        return cls.query.filter_by(payment_id=payment_id).first()


class Advice(db.Model):
    __tablename__ = "advice"
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    content = db.Column(db.String(512))
    create_time = db.Column(db.DateTime, default=datetime.utcnow())
