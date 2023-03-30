from book.views import *
from book.models import *



if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

    app.run(debug=True)
