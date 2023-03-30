from book import app
from book.dbModels import *
from book.views import *



if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.run(debug=True)
