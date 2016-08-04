import threading

from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379//')


@app.task
def build(info):
    print threading.current_thread().ident, info, type(info)
