# encoding:utf-8
import hashlib

import os

import flask
from flask import send_from_directory, redirect, render_template

import config
from book import request, cache, app, db, Blueprint
# user = Blueprint('user', __name__)
import logging
from book.ApiResponse import APIResponse


@app.route("/")
def home():
    # logging.error(app.template_folder)
    return "欢迎关注公众号：sendtokindles 下载电子书"
