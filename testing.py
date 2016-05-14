import os.path

from jinja2 import Environment, PackageLoader
from pkg_resources import get_provider

from builder import environments

if __name__ == '__main__':
    provider = get_provider('builder')
    print provider.has_resource("templates/conf.py.tmpl")
    env = Environment(loader=PackageLoader('builder', 'templates'))

    template = env.get_template('conf.py.tmpl')
    # print template.render()

    # $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
    # sphinx-build -b html -d _build/doctrees . _build/html

    doc = os.path.dirname(__file__)
    cmd = environments.BuildCommand("sphinx-build -b html -d _build/doctrees . _build/html".split(),
                                    cwd=os.path.join(doc, 'docs'))
    cmd.run()
