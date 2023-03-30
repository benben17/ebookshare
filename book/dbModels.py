# coding: utf-8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from book import app

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

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    author = db.Column(db.String(128))
    publisher = db.Column(db.String(128))
    extension = db.Column(db.String(128))
    filesize = db.Column(db.String(64))
    language = db.Column(db.String(24))
    publish_year = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    isbn = db.Column(db.String(30))
    bookext = relationship('Bookurl',  backref=backref('books'), uselist=False)


class Bookurl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey('books.id'))
    book_download_url = db.Column(db.String(128))

with app.app_context():
    db.create_all()