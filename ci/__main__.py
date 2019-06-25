import click
from subprocess import check_call

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
    check_call([
        "edm", "install", "-e", env_name,
        "--yes"] + ADDITIONAL_CORE_DEPS)

    edm_run(env_name, ["pip", "install", "-e", "."])


@cli.command(help="Run the tests")
@python_version_option
def test(python_version):
    env_name = get_env_name(python_version)

    edm_run(env_name, ["python", "-m", "unittest", "discover", "-v"])


@cli.command(help="Run flake")
@python_version_option
def flake8(python_version):
    env_name = get_env_name(python_version)

    edm_run(env_name, ["flake8", "."])


@cli.command(help="Runs the coverage")
@python_version_option
def coverage(python_version):
    env_name = get_env_name(python_version)

    edm_run(env_name, ["coverage", "run", "-m", "unittest", "discover"])
    edm_run(env_name, ["pip", "install", "codecov"])
    edm_run(env_name, ["codecov"])


@cli.command(help="Builds the documentation")
@python_version_option
def docs(python_version):
    env_name = get_env_name(python_version)

    edm_run(env_name, ["make", "html"], cwd="doc")


def get_env_name(python_version):
    return "force-py{}".format(remove_dot(python_version))


def remove_dot(python_version):
    return "".join(python_version.split('.'))


def edm_run(env_name, cmd, cwd=None):
    check_call(["edm", "run", "-e", env_name, "--"]+cmd, cwd=cwd)


if __name__ == "__main__":
    cli()
