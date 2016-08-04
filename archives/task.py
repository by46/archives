from __future__ import print_function

import os
import tempfile
from urlparse import urlparse

from git import Repo

from archives import app
from archives import celery


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def build_workspace(repository):
    opt = urlparse(repository)
    parts = opt.path.split('/')
    group = parts[-2]
    project_slug = parts[-1]
    project_slug = project_slug.split('.')[0]

    tmp_dir = os.path.join(tempfile.gettempdir(), app.import_name, group.lower(), project_slug.lower())
    ensure_dir(tmp_dir)
    return os.path.join(tmp_dir, 'git')


@celery.task
def build(branch, username, email, repository):
    workspace = build_workspace(repository)
    if os.path.exists(workspace):
        repo = Repo(workspace)
        origin = repo.remotes['origin']
        origin.pull()
    else:
        Repo.clone_from(repository, workspace, branch='master')

    print(branch, username, email, repository)
