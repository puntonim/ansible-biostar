import os
from django.conf import settings


# Set the log folder.
log_folder = os.path.join(settings.LIVE_DIR, 'logs')
if not os.path.exists(log_folder):
    os.mkdir(log_folder)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s.%(funcName)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },

        'ratelimit': {
            '()': 'biostar.settings.logger.RateLimitFilter',
        }
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'ratelimit'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },

        'simple':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'rotatingfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_folder, 'biostar.log'),
            'mode': 'a',
            'maxBytes': 1048576,  # max 1 Mbyte
            'backupCount': 0,  # max 1 file
            'formatter': 'verbose',
        },
    },

    'loggers': {
        '': {
            'handlers': ['rotatingfile'],
            'level': 'INFO',
            'propagate': True,
        },

        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },

        'biostar':{
            'level': 'INFO',
            'handlers': ['console'],
        },

        'command':{
            'level': 'INFO',
            'handlers': ['console'],
        },

       'simple-logger':{
            'level': 'INFO',
            'handlers': ['simple'],
        },
    }

}

