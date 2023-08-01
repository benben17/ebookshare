# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present benben
"""
from importlib import import_module

from flask import render_template, redirect
from book import app
from book.pay import paypal

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


modules = ['user', 'ebook', 'feed', 'wechat', 'rssbook', 'googleUser']
for model_name in modules:
    model = import_module(f"{app.name}.views.{model_name}")
    app.register_blueprint(model.blueprint)


app.register_blueprint(paypal.blueprint)
