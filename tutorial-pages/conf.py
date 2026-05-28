project = "TRex Tutorials"
author = "Angela Albi, Tristan Walter"
copyright = "2026"

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "names.rst"]

numfig = True
suppress_warnings = ["ref.doc", "ref.ref"]

html_theme = "sphinx_clarity_theme"
html_static_path = ["_static"]
html_favicon = "_static/icons/TRexA_installer_2048.png"
default_dark_mode = True

rst_prolog = """
.. role:: blueText
.. role:: greenText
"""

from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes
from sphinx.addnodes import pending_xref

def green_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    set_classes(options)
    text = utils.unescape(text)
    node = nodes.inline(rawtext, text, classes=['green-text'])
    return [node], []

def param_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Create a cross-reference to a function defined in parameters_trex.rst.
    Example: :param:`adaptive_threshold_scale`
    """
    set_classes(options)
    # Create a pending_xref node that references a Python function
    node = pending_xref(
        rawsource=rawtext,
        refdomain='py',  # Use the Python domain
        reftype='func',  # Use the function reference type
        reftarget=text,  # The target is the function name
        modname=None,
        classname=None,
        refexplicit=False,
        refwarn=True,
        classes=['param-reference'],
        **options
    )
    node += nodes.literal(text, text)
    return [node], []

def setup(app):
    app.add_css_file('custom.css')  # may also be an URL
    app.add_js_file('copy-button.js')
    app.add_role('green', green_role)
    app.add_role('param', param_role)  # So you can do :param:`my_parameter`
