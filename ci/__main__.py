import click
import contextlib
import os
import subprocess
import tempfile

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
    returncode = subprocess.call([
        "edm", "install", "-e", env_name,
        "--yes"] + ADDITIONAL_CORE_DEPS)

    if returncode:
        raise click.ClickException("Error while installing EDM dependencies.")

    returncode = edm_run(env_name, ["pip", "install", "-e", "."])


@cli.command(help="Run the tests")
@python_version_option
def test(python_version):
    env_name = get_env_name(python_version)

    with _hide_user_saved_state(env_name):
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

    with _hide_user_saved_state(env_name):
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
def docs(python_version):
    env_name = get_env_name(python_version)

    returncode = edm_run(env_name, ["make", "html"], cwd="doc")
    if returncode:
        raise click.ClickException(
            "There were errors while building the documentation.")


def get_env_name(python_version):
    return "force-py{}".format(remove_dot(python_version))


def remove_dot(python_version):
    return "".join(python_version.split('.'))


def edm_run(env_name, cmd, cwd=None):
    return subprocess.call(["edm", "run", "-e", env_name, "--"]+cmd, cwd=cwd)


def edm_run_output(env_name, cmd, cwd=None):
    return subprocess.check_output(
        ["edm", "run", "-e", env_name, "--"]+cmd, cwd=cwd)


@contextlib.contextmanager
def _hide_user_saved_state(env_name):
    """ Context manager that backs up the user's application_memento file, if
    it exists and if it's possible.
    Note: this is lenient: if backing up is not possible, it's just skipped
    (and the failure is reported to the user).
    """
    issues = False
    backed_up = False
    tempdir = tempfile.gettempdir()

    # try to get the state location
    script = os.path.join("ci", "scripts", "state_location.py")
    try:
        expected_loc = edm_run_output(
            env_name, ["python", script])
    except subprocess.CalledProcessError:
        expected_loc = ""
        issues = True
    expected_loc = expected_loc.strip()

    # try to make a backup if needed
    if expected_loc and os.path.isfile(expected_loc) and not issues:
        backup_loc = os.path.join(
            tempdir,
            os.path.basename(expected_loc)+".backup")
        try:
            os.rename(expected_loc, backup_loc)
            backed_up = True
            click.echo(
                "The local application_memento file was backed up "
                "to a temporary location: {!r}".format(backup_loc)
            )
        except EnvironmentError:
            issues = True

    # yield the context, then clean up or report failure
    try:
        yield
    finally:
        if issues:
            click.echo(
                "It wasn't possible to back-up the user state file (if any).")
        if backed_up:
            os.rename(backup_loc, expected_loc)
            click.echo(
                "The local application_memento file was restored."
            )


if __name__ == "__main__":
    cli()
