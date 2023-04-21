# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present AppSeed.us
"""

bind = '0.0.0.0:8000'
# workers = 2
threads = 2
worker_class = 'gevent'
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
pidfile = "logs/gunicorn.pid"
timeout = 60
