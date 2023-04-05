
from flask import Flask
from book import app
from book.schedule import *



if __name__ == '__main__':
    app.logger.info("aaa")
    app.run(debug=True,threaded=True,use_reloader=False)
