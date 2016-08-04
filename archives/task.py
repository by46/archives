from __future__ import print_function
import os.path
import os
from git import Repo

from archives import celery


def build_workspace(repository):
    return 'd:\\tmp\\taxi'


@celery.task
def build(branch, username, email, repository):
    workspace = build_workspace(repository)
    if os.path.exists(workspace):
        repo = Repo(workspace)
    else:
        repo = Repo.clone_from(repository, 'd:\\tmp\\taxi', branch='master')

    print(branch, username, email, repository)
