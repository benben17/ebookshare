# from book.views import user, feed, wechat, myfeed
import os

from book import app
from book.schedule import *
from gevent import pywsgi

if __name__ == '__main__':
    # print(app.url_map)
    print(os.getenv('DEBUG'))
    app.run(debug=True,threaded=True,use_reloader=False, port=5000)
    # server = pywsgi.WSGIServer(('0.0.0.0',6000),app)
    # server.serve_forever()