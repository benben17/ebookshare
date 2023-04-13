# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present benben
"""
from flask import render_template, request, redirect

from book import app


@app.route("/404")
def page_404():
    # logging.error(app.template_folder)
    return render_template("404.html")


@app.route("/")
def home():
    # logging.error(app.template_folder)
    return redirect('/404')


@app.route("/no_att")
def kindle_no_att():
    # print(request.url)
    # logging.error(app.template_folder)
    return render_template("kindle_no_att.html")
