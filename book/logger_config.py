import os
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

import logging

# Import Log Base Path From Config File
# The output should be something like this
# log_base_path = "/var/log/"

log_base_path = "./logs"


def init_logging(app):
    """
    Initialize logging
    """
    logfile = f"{os.path.dirname(app.root_path)}/logs/books.log"
    logging.basicConfig(level=logging.INFO)
    handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100, backupCount=5)  # 最大100M
    """Time, log level, log file, line number, message"""
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


logging_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'JSONPERLINE': {
            'format': '%(message)s'
        },

    },
    'handlers': {
        'audit_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_base_path, 'audit_log.log'),
            'formatter': 'JSONPERLINE'
        }
    },
    'loggers': {
        'audit_log': {
            'handlers': ['audit_log'],
            'level': 'INFO'
        }
    }
}

# dictConfig(logging_dict)
