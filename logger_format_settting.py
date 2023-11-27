import logging, logging.config

def initialize():
    global MY_LOGGING_FORMAT
    MY_LOGGING_FORMAT = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'normal': {  # the name of formatter
                'format': '[%(asctime)s];%(levelname)s;%(name)s;%(process_name)s;%(message)s'
            },
            'simple': {  # the name of formatter
                'format': '%(levelname)s;%(process_name)s;%(message)s'
            },
        },
        'handlers': {
            'debug_file': {  # the name of handler
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/debug.log',
                'mode':'+a',
                'maxBytes': 5*1024*1024,
                'backupCount': 2,
                'delay': 0,
                'encoding': 'utf-8',
                'formatter': 'normal'
            },
            'error_file': {  # the name of handler
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/error.log',
                'mode':'+a',
                'maxBytes': 5*1024*1024,
                'backupCount': 2,
                'delay': 0,
                'encoding': 'utf-8',
                'formatter': 'normal'
            },
        },
        'loggers': {
            'debug': {  # the name of logger
                'handlers': ['debug_file'],  # the name of handler to be used
                'level': 'DEBUG',  # logging level
                'propagate': True
            },
            'error': {  # the name of logger
                'handlers': ['error_file'],  # the name of handler to be used
                'level': 'ERROR',  # logging level
                'propagate': True,
            }
        },
    }

    logging.config.dictConfig(MY_LOGGING_FORMAT)