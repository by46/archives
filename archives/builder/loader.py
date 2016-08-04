import builder.backends

# Managers
sphinx = builder.backends.sphinx

BUILDER_BY_NAME = {
    # Possible HTML Builders
    'sphinx': sphinx.HtmlBuilder,
    'sphinx_htmldir': sphinx.HtmlDirBuilder,
    'sphinx_singlehtml': sphinx.SingleHtmlBuilder,
    # Other Sphinx Builders
    'sphinx_pdf': sphinx.PdfBuilder,
    'sphinx_epub': sphinx.EpubBuilder,
    'sphinx_search': sphinx.SearchBuilder,
    'sphinx_singlehtmllocalmedia': sphinx.LocalMediaBuilder
}


def get_builder_class(name):
    return BUILDER_BY_NAME[name]
