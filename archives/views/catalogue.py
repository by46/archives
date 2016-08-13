from flask import render_template

from archives import bp


@bp.route('/')
def catalogue():
    projects = [{'user': 'dfis', 'name': 'Recipe'},
                {'user': 'DFIS', 'name': 'Archives'}]
    return render_template('catalogue.html', projects=projects)


@bp.route('/<user>/<name>')
def project(user=None, name=None):
    doc = {'user': user, 'name': name}
    versions = ["latest", '0.0.1', '0.0.2']
    return render_template('project.html', project=doc, versions=versions)
