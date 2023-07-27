import os
from logging.config import dictConfig

# Import Log Base Path From Config File
# The output should be something like this
# log_base_path = "/var/log/"

log_base_path = "./logs"

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
