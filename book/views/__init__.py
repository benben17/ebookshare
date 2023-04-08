from flask import render_template

from . import *
from .. import app


@app.route("/404")
def page_404():
    # logging.error(app.template_folder)
    return render_template("404.html")
