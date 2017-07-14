import os

from setuptools import setup, find_packages

# Setup version
VERSION = '0.1.0'


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
        "stevedore >= 1.24.0"
        ],
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            ('force-wfmanager = force_wfmanager.run:main')
        ],
        "force.bdss.extensions": [
            "mco = force_bdss.mco.multi_criteria_optimizers_plugin:"
            "MultiCriteriaOptimizersPlugin",
            "data_source = force_bdss.data_sources.data_sources_plugin:"
            "DataSourcesPlugin",
        ]
    },
)
