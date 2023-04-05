import logging

from flask import Flask

from book import app
from book.schedule import *



if __name__ == '__main__':

    print(app.url_map)
    print(app.static_folder)
    app.run(debug=True,threaded=True,use_reloader=False)
