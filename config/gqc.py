# CELERY
CELERY_BROKER_URL = 'redis://10.16.78.86:6380'
CELERY_RESULT_BACKEND = 'redis://10.16.78.86:6380'

# NGINX STATIC HOME
DOC_HOME = '/opt/data'


# Flask-Log Settings
LOG_LEVEL = 'debug'
LOG_FILENAME = "/var/archives/error.log"
LOG_ENABLE_CONSOLE = False