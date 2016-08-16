from flask import render_template

from archives import bp
from archives.db import DataAccess


@bp.route('/')
def catalogue():
    projects = [{'user': 'dfis', 'name': 'Recipe'},
                {'user': 'DFIS', 'name': 'Archives'}]
    projects = DataAccess.get_projects()
    return render_template('catalogue.html', projects=projects)


@bp.route('/<user>/<name>/')
def project(user=None, name=None):
    doc = {'user': user, 'name': name}
    versions = DataAccess.get_versions(user, name)
    return render_template('project.html', project=doc, versions=versions)
