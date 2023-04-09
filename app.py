# from book.views import user, feed, wechat, myfeed
import os

from book import *
from book.schedule import *


if __name__ == '__main__':
    # print(app.url_map)
    app.run(debug=True,threaded=True,use_reloader=False, port=8000)
