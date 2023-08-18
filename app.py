# from book.views import user, feed, wechat, myfeed
import os

from book import app
from book.schedule import *
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    # print(app.url_map)
    http_server = WSGIServer(('0.0.0.0', os.getenv("PORT")), app)
    http_server.serve_forever()
