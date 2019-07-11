# -*- coding: utf-8 -*-
#
# FORCE documentation build configuration file, created by
# sphinx-quickstart on Mon Feb 02 16:26:16 2015.

import sphinx.environment
from docutils.utils import get_source_line
import sys
import os

def _warn_node(self, msg, node, **kwargs):
    if not msg.startswith('nonlocal image URI found:'):
        self._warnfunc(msg, '%s:%s' % get_source_line(node), **kwargs)

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )

from force_wfmanager.version import __version__ as RELEASE

sphinx.environment.BuildEnvironment.warn_node = _warn_node

def mock_modules():
    import sys

    from unittest.mock import MagicMock

    try:
        import tables
    except ImportError:
        MOCK_MODULES = ['tables']
    else:
        MOCK_MODULES = []

    try:
        import numpy
    except ImportError:
        MOCK_MODULES.append('numpy')

    class Mock(MagicMock):

        @classmethod
        def __getattr__(cls, name):
            return Mock()

        def __call__(self, *args, **kwards):
            return Mock()

    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
    print('mocking {}'.format(MOCK_MODULES))

# mock_modules()

# General Configuration
# ---------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'traits.util.trait_documenter'
]

try:
    import enthought_sphinx_theme

    html_theme_path = [enthought_sphinx_theme.theme_path]
    html_theme = 'enthought'
except ImportError as exc:
    import warnings
    msg = '''Can't find Enthought Sphinx Theme, using default.
                Exception was: {}
                Enthought Sphinx Theme can be downloaded from
                https://github.com/enthought/enthought-sphinx-theme'''
    warnings.warn(RuntimeWarning(msg.format(exc)))


templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'FORCE Workflow Manager'
copyright = u'2019, FORCE, EU H2020 Project'
version = ".".join(RELEASE.split(".")[0:3])
release = RELEASE
exclude_patterns = []
pygments_style = 'sphinx'
html_theme = 'classic'
html_static_path = ['_static']
htmlhelp_basename = 'Forcedoc'
intersphinx_mapping = {'http://docs.python.org/': None}
