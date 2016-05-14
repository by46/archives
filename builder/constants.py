import os
import re

SPHINX_TEMPLATE_DIR = os.path.join('templates', 'sphinx')
MKDOCS_TEMPLATE_DIR = os.path.join('templates', 'mkdocs')
SPHINX_STATIC_DIR = os.path.join(SPHINX_TEMPLATE_DIR, '_static')

PDF_RE = re.compile('Output written on (.*?)')
