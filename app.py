from book import app
from book.dbModels import *
from book.views import *
from book.taskSchedule import *
import multiprocessing
workers = multiprocessing.cpu_count() * 2 +1



if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.run(debug=True,threaded=True)
