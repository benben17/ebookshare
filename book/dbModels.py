# coding: utf-8
from datetime import datetime
from book import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    role = db.Column(db.String(120))
    srole = db.Column(db.Integer, default=0)
    hash_pass = db.Column(db.String(200))
    kindle_email = db.Column(db.String(120))
    wx_openid = db.Column(db.String(64),unique=True)
    upload_times = db.Column(db.Integer, default=0)
    download_times = db.Column(db.Integer, default=0)
    feed_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Integer, default=0)
    expires = db.Column(db.DateTime)  # 超过了此日期后账号自动停止推送
    create_time = db.Column(db.DateTime, default=datetime.now())

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
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book_download_url = db.Column(db.String(512))


class Userlog(db.Model):
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

class Librss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    url = db.Column(db.String(300))
    isfulltext = db.Column(db.Integer)
    desc = db.Column(db.String(300))
    category = db.Column(db.String(64),index=True)
    creator = db.Column(db.String(64))
    created_time = db.Column(db.DateTime, default=datetime.now())
    subscribed = db.Column(db.Integer, default=0)  # for sort
    invalid_date = db.Column(db.DateTime, default=datetime.now())  # some one reported it is a invalid link

    def __repr__(self):
        return self.title

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'isfulltext': self.isfulltext,
            'desc': self.desc,
            'category': self.category,
            'creator': self.creator,
            'created_time': self.created_time.isoformat() if self.created_time is not None else None,
            'subscribed': self.subscribed,
            'invalid_date': self.invalid_date.isoformat() if self.invalid_date is not None else None
        }

    # return all categories in database

class MyFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rss_id = db.Column(db.Integer, index=True)
    title = db.Column(db.String(64))
    url = db.Column(db.String(300))
    isfulltext = isfulltext = db.Column(db.Integer)
    wx_openid = db.Column(db.String(64),index=True)  # 微信id
    user_id = db.Column(db.Integer,index=True)
    feed_time = db.Column(db.DateTime, default=datetime.now())  # 订阅时间
    created_time = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'isfulltext': self.isfulltext,
            'time': self.feed_time if self.feed_time is not None else None ,
            'created_time': self.created_time.isoformat() if self.created_time is not None else None
        }


