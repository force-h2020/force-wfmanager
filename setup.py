import os
from setuptools import setup, find_packages

# Setup version
VERSION = '0.2.0.dev0'


# Read description
with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()


def write_version_py():
    filename = os.path.join(
        os.path.dirname(__file__),
        'force_wfmanager',
        'version.py')
    ver = "__version__ = '{}'\n"
    with open(filename, 'w') as fh:
        fh.write(ver.format(VERSION))


write_version_py()


# main setup configuration class
setup(
    name='force-wfmanager',
    version=VERSION,
    author='FORCE, EU H2020 Project',
    description='Workflow manager',
    long_description=README_TEXT,
    install_requires=[
        "envisage >= 4.6.0",
        "stevedore >= 1.24.0",
        "numpy >= 1.11.0",
        "cython >= 0.25",
        "chaco >= 4.6.1",
        "pyzmq >= 16.0.0",
        'futures >= 3.1.1',
        "six >= 1.10.0",
        'force_bdss >= 0.2.0.dev0'
    ],
    packages=find_packages(),
    package_data={'force_wfmanager.left_side_pane': 'icons/*'},
    entry_points={
        'gui_scripts': [
            'force_wfmanager = force_wfmanager.cli.run:force_wfmanager'
        ],
        "force.bdss.extensions": [
            "ui_notification = "
            "force_wfmanager.plugins.ui_notification.ui_notification_plugin:"
            "UINotificationPlugin",
        ]
    },
)
