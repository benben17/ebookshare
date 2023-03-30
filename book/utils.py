# -*-coding: utf-8-*-
import os.path
from pathlib import Path


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_ebook_ext(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'mobi', 'azw3', 'epub'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_name(file):
    file_suffix = str(Path(file).suffix)
    return os.path.basename(file).replace(file_suffix, "")

def get_file_suffix(file):
    if '.' in file:
        _, suffix = file.rsplit('.', 1)
        return suffix.lower()

import os



