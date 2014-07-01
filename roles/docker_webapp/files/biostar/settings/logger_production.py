# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

import os
from django.conf import settings


# Set the log folder.
log_folder = os.path.join(settings.LIVE_DIR, 'logs')
if not os.path.exists(log_folder):
    os.mkdir(log_folder)


class RateLimitFilter(object):

    def filter(self, record):
        from django.core.cache import cache
        TIMEOUT = 600
        CACHE_KEY = "error-limiter"

        exists = cache.get(CACHE_KEY)
        if not exists:
            cache.set(CACHE_KEY, 1, TIMEOUT)

        return not exists

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

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

        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_folder, 'biostar.log'),
            'mode': 'a',
            'formatter': 'verbose',
         },
    },

    'loggers': {
        '': {
            'handlers': ['file'],
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

