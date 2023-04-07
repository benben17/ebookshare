from flask import jsonify, g, flash
from flask_login import current_user

from book import app, request, Librss, MyFeed, db
from book.ApiResponse import APIResponse
from book.utils import model_to_dict


@app.before_request
def before_request():
    g.user = current_user

@app.route('/api/rss/libray',  methods=['GET'])
def librss():
    librss = Librss.query.filter().all()
    return APIResponse.success(data=[model_to_dict(rss) for rss in librss ])

