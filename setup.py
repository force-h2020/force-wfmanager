import os
from setuptools import setup, find_packages

# Setup version
VERSION = '0.4.0dev0'


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
    packages=find_packages(),
    package_data={'force_wfmanager.left_side_pane': 'icons/*'},
    entry_points={
        'gui_scripts': [
            'force_wfmanager = force_wfmanager.gui.run:force_wfmanager'
        ],
        "force.bdss.extensions": [
            "ui_notification = "
            "force_wfmanager.plugins.ui_notification.ui_notification_plugin:"
            "UINotificationPlugin",
        ]
    },
    install_requires=[
        "force_bdss >= 0.3.0",
    ]
)
