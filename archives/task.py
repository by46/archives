from __future__ import print_function

import os
import re
import shutil
import tempfile
from urlparse import urlparse

from fabric.api import lcd
from fabric.api import local
from git import Repo

from archives import app
from archives import celery

_RE_VERSION = "^\s*version\s*=\s*[\"']\s*(.*)[\"'].*"


# TODO(benjamin): remove this code in matrix
def rebuild_repository(repository):
    opt = urlparse(repository)
    return '{0}://10.16.77.53{1}'.format(opt.scheme, opt.path)


def find_version():
    home = os.path.join(__file__, '..', '..', 'doc', 'conf.py')
    version = '0.0.1'
    if os.path.exists(home):
        with open(home, 'rb') as f:
            for line in f:
                match = re.match(_RE_VERSION, line)
                if match:
                    version, = match.groups()

    return version


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    ensure_dir(parent)


def parse_group_project(repository):
    opt = urlparse(repository)
    parts = opt.path.split('/')
    group = parts[-2]
    project_slug = parts[-1]
    project_slug = project_slug.split('.')[0]
    return group, project_slug


def build_workspace(repository):
    group, project_slug = parse_group_project(repository)
    sys_temp_dir = tempfile.gettempdir()
    # TODO(benjamin): remove debugging code
    # sys_temp_dir = 'd:\\tmp\\benjamn'
    tmp_dir = os.path.join(sys_temp_dir, app.import_name, group.lower(), project_slug.lower())
    ensure_dir(tmp_dir)
    return os.path.join(tmp_dir, 'git')


@celery.task
def build(branch, username, email, repository):
    app.logger.info('Building %s, %s %s on branch %s', repository, username, email, branch)
    workspace = build_workspace(repository)
    app.logger.info('on workspace %s', workspace)
    if os.path.exists(workspace):
        app.logger.info('Fetch project')
        repo = Repo(workspace)
        origin = repo.remotes['origin']
        origin.pull()
    else:
        app.logger.info('Clone project')
        Repo.clone_from(rebuild_repository(repository), workspace, branch='master')

    doc_path = os.path.join(workspace, 'doc')
    if os.path.exists(doc_path):
        app.logger.info('enter doc path %s', doc_path)
        with lcd(doc_path):
            try:
                local('make html')
                group, project_slug = parse_group_project(repository)
                versions = [find_version(), 'latest']
                for version in versions:
                    nginx_doc_path = os.path.join(app.config['DOC_HOME'], group.lower(), project_slug.lower(), version)
                    if os.path.isdir(nginx_doc_path):
                        shutil.rmtree(nginx_doc_path)
                    ensure_parent_dir(nginx_doc_path)
                    shutil.copytree(os.path.join(doc_path, '_build', 'html'), nginx_doc_path)
            except Exception as e:
                # TODO(benjamin): send notice send to user_name with user_email
                app.logger.exception(e)
                raise e
