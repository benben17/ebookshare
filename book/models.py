# coding: utf-8
from flask import Flask
from flask_principal import Principal
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
# load the extension
principals = Principal(app)
db = SQLAlchemy(app)
# db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120))
    role = db.Column(db.String(120))
    srole = db.Column(db.Integer, default=0)
    hash_pass = db.Column(db.String(200))

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


# dbs = db.Table('dbs',
#         db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
#         db.Column('book_url_id', db.Integer, db.ForeignKey('bookurl.id'))
#     )
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    author = db.Column(db.String(64))
    publisher = db.Column(db.String(128))
    extension = db.Column(db.String(128))
    filesize = db.Column(db.String(128))
    language = db.Column(db.String(128))
    publish_year = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    isbn = db.Column(db.String(128))
    # dbs = db.relationship('BookUrl', secondary=dbs, backref=db.backref('bookdownloadurl', lazy='dynamic'))


class BookUrl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    book_download_url = db.Column(db.String(128))


with app.app_context():
    db.create_all()
    user=User.query.filter(User.name == 'admin').first()
    print(user)