import time
from distutils.version import LooseVersion

import redis
from flask import g

from archives import app


def get_db():
    if not hasattr(g, 'redis'):
        g.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])
    return g.redis


class DataAccess(object):
    PROJECTS = "archives:projects"

    # -------------------------------------
    # projects
    # -------------------------------------
    @staticmethod
    def add_project(user, name, version):
        conn = get_db()
        project_name = '{0}_{1}'.format(user.lower(), name.lower())
        conn.sadd(DataAccess.PROJECTS, project_name)

        key = 'archives:versions:{0}'.format(project_name)
        conn.sadd(key, version.lower())

        key = 'archives:project:{0}'.format(project_name)
        info = dict(user=user, name=name, latest_date=time.ctime())
        conn.hmset(key, info)

    @staticmethod
    def get_projects():
        conn = get_db()
        projects = conn.smembers(DataAccess.PROJECTS)
        items = []
        for project in projects:
            user, name = project.split('_', 1)
            items.append(dict(user=user, name=name))
        return items

    @staticmethod
    def get_versions(user, name):
        conn = get_db()
        key = 'archives:versions:{0}_{1}'.format(user.lower(), name.lower())

        versions = conn.smembers(key)
        if versions:
            versions = sorted([LooseVersion(version) for version in versions], reverse=True)
            return ['latest'] + map(str, versions[1:])
        return []
