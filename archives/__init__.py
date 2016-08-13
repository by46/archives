"""Archives

"""
import os

from celery import Celery
from flask import Blueprint
from flask import Flask
from flask_log import Log

__version__ = '0.0.1'
__author__ = 'benjamin.c.yan'

app = Flask(__name__)
bp = Blueprint('archives', __name__, url_prefix='/docs', static_folder='static')


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.from_object('config.default')
key = 'ENV'
if key not in os.environ:
    os.environ[key] = 'development'

env = os.environ.get(key)
app.config.from_object('config.{0}'.format(env.lower()))

app.config['VERSION'] = __version__

celery = make_celery(app)

from archives import views

app.register_blueprint(bp)

# Config logger
Log(app)
print app.url_map
from archives.db import DataAccess
