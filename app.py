# from book.views import user, feed, wechat, myfeed
import os

from book import app
from book.schedule import *


if __name__ == '__main__':
    # print(app.url_map)
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
