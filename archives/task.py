from __future__ import print_function

from archives import celery


@celery.task
def build(branch, username, email, repository):
    print(branch, username, email, repository)
