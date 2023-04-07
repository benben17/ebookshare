from book.views import user, feed, wechat, myfeed
from book.schedule import *
from book import *




if __name__ == '__main__':
    app.run(debug=True,threaded=True,use_reloader=False,port=8000)
