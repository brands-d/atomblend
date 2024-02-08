from importlib.util import find_spec
from subprocess import call
from sys import executable

from .src import __directory__


def install_dependencies():
    install_required = False
    for requirement in ("ase", "skimage"):
        package_name = requirement.split("==")[0]
        if find_spec(package_name) is None:
            install_required = True
            break

    if install_required:
        call([str(executable), "-m", "ensurepip", "--user"])
        call([str(executable), "-m", "pip", "install", "--upgrade", "pip"])
        call(
            [
                str(executable),
                "-m",
                "pip",
                "install",
                "--user",
                "-r",
                "requirements.txt",
            ]
        )
