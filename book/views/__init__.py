# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present benben
"""
from flask import render_template

from book import app


@app.route("/404")
def page_404():
    # logging.error(app.template_folder)
    return render_template("404.html")


@app.route("/")
def home():
    # logging.error(app.template_folder)
    return "欢迎关注公众号：sendtokindles 下载电子书"



