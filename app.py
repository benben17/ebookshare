
from flask import Flask
# from book import app
from book.schedule import *
from book import *



if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True,threaded=True,use_reloader=False,port=8000)
