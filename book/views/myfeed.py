from flask import jsonify

from book import app, request, Librss
from book.ApiResponse import APIResponse
from book.utils import model_to_dict


@app.route('/api/librss',  methods=['GET'])
def librss():
    librss = Librss.query.filter().all()

    return APIResponse.success(data=[model_to_dict(rss) for rss in librss ])