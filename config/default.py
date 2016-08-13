HTTP_HOST = ''
HTTP_PORT = 8080

BUILD_BRANCH = 'master'

# Celery settings
CELERY_BROKER_URL = 'redis://10.16.78.86:6379'
CELERY_RESULT_BACKEND = 'redis://10.16.78.86:6379'

# NGINX
DOC_HOME = '/opt/data'

# WSGI Settings
WSGI_LOG = 'default'

# Flask-Log Settings
LOG_LEVEL = 'debug'
LOG_FILENAME = "logs/error.log"
LOG_BACKUP_COUNT = 10
LOG_MAX_BYTE = 1024 * 1024 * 10
LOG_FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ENABLE_CONSOLE = True


# REDIS Settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
