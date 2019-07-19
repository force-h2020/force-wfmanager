import click
import os
import shutil
import subprocess

DEFAULT_PYTHON_VERSION = "3.6"
PYTHON_VERSIONS = ["3.6"]

ADDITIONAL_CORE_DEPS = [
    "pyface==6.1.0-2",
    "pygments==2.2.0-1",
    "pyqt==4.11.4-7",
    "qt==4.8.7-10",
    "sip==4.17-4",
    "traitsui==6.1.1-1",
    "numpy==1.15.4-2",
    "chaco==4.7.2-3",
    "pyzmq==16.0.0-7",
    "mock==2.0.0-3"
]

ADDITIONAL_PIP_DEPS = [
    # FIXME: Using pyface from master to take advantage of this not yet
    #        released bugfix: enthought/pyface#409
    'git+https://github.com/enthought/pyface.git'
    '@c3fee1b80c73c3b95b37be5023a3fd03a2a885d3'
]


@click.group()
def cli():
    pass


python_version_option = click.option(
    '--python-version',
    default=DEFAULT_PYTHON_VERSION,
    type=click.Choice(PYTHON_VERSIONS),
    show_default=True,
    help="Python version for the environment")


@cli.command(name="install", help="Creates the execution environment")
@python_version_option
def install(python_version):
    env_name = get_env_name(python_version)
    returncode = subprocess.call([
        "edm", "install", "-e", env_name,
        "--yes"] + ADDITIONAL_CORE_DEPS)

    if returncode:
        raise click.ClickException("Error while installing EDM dependencies.")

    for dep in ADDITIONAL_PIP_DEPS:
        returncode = edm_run(env_name, ["pip", "install", dep])
        if returncode:
            raise click.ClickException(
                "Error while installing {!r} through pip.".format(dep))

    returncode = edm_run(env_name, ["pip", "install", "-e", "."])
    if returncode:
        raise click.ClickException("Error while installing the local package.")


@cli.command(help="Run the tests")
@python_version_option
def test(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(
        env_name, ["python", "-m", "unittest", "discover", "-v"])

    if returncode:
        raise click.ClickException("There were test failures.")


@cli.command(help="Run flake")
@python_version_option
def flake8(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(env_name, ["flake8", "."])
    if returncode:
        raise click.ClickException(
            "Flake8 exited with exit status {}".format(returncode))


@cli.command(help="Runs the coverage")
@python_version_option
def coverage(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(
        env_name, ["coverage", "run", "-m", "unittest", "discover"])
    if returncode:
        raise click.ClickException("There were test failures.")

    returncode = edm_run(env_name, ["pip", "install", "codecov"])
    if not returncode:
        returncode = edm_run(env_name, ["codecov"])

    if returncode:
        raise click.ClickException(
            "There were errors while installing and running codecov.")


@cli.command(help="Builds the documentation")
@python_version_option
@click.option('--apidoc-only', is_flag=True, help="Only generate API docs.")
@click.option(
    '--html-only', is_flag=True,
    help="Only generate HTML documentation (requires API docs in source/api)."
)
def docs(python_version, apidoc_only, html_only):
    if apidoc_only and html_only:
        raise click.ClickException("Conflicting request in the invocation.")

    env_name = get_env_name(python_version)
    doc_api = os.path.abspath(os.path.join("doc", "source", "api"))
    package = os.path.abspath("force_wfmanager")

    if not html_only:
        click.echo("Generating API doc")
        if os.path.exists(doc_api):
            shutil.rmtree(doc_api)
        returncode = edm_run(
            env_name, ['sphinx-apidoc', '-o', doc_api, package, '*tests*'])
        if returncode:
            raise click.ClickException(
                "There were errors while building the API doc.")

    if not apidoc_only:
        click.echo("Generating HTML")
        returncode = edm_run(env_name, ["make", "html"], cwd="doc")
        if returncode:
            raise click.ClickException(
                "There were errors while building HTML documentation.")


def get_env_name(python_version):
    return "force-py{}".format(remove_dot(python_version))


def remove_dot(python_version):
    return "".join(python_version.split('.'))


def edm_run(env_name, cmd, cwd=None):
    return subprocess.call(["edm", "run", "-e", env_name, "--"]+cmd, cwd=cwd)


if __name__ == "__main__":
    cli()
