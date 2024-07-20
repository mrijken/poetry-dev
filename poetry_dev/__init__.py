"""
command line interface definitions
"""
import pathlib
import subprocess
from typing import Dict, Union
import warnings

import tomlkit
import typer

warnings.warn("This package is not maintained anymore", DeprecationWarning)

app = typer.Typer()

Requirement = Union[str, Dict[str, str]]
Dependencies = Dict[str, Requirement]


def get_pyproject_path(base_dir=pathlib.Path(".")) -> pathlib.Path:
    """
    Get the path to the pyproject.toml file in the given `base_dir` (which
    defailts to current directry)
    """
    return base_dir / "pyproject.toml"


def get_version(base_dir=pathlib.Path(".")) -> str:
    """get the version from pyproject.toml"""
    pyproject_path = get_pyproject_path(base_dir)

    pyproject = tomlkit.parse(pyproject_path.read_text())
    return pyproject["tool"]["poetry"]["version"]


def get_dependencies() -> Dependencies:
    """get the poerty dependencies from pyproject.toml"""
    pyproject_path = get_pyproject_path()

    pyproject = tomlkit.parse(pyproject_path.read_text())
    return pyproject["tool"]["poetry"]["dependencies"]


def set_changed_dependencies(changed_dependencies: Dependencies) -> None:
    """update the poerty dependencies in pyproject.toml"""
    pyproject_path = get_pyproject_path()

    # remove the changed dependencies
    pyproject = tomlkit.parse(pyproject_path.read_text())
    dep = pyproject["tool"]["poetry"]["dependencies"]
    for name in changed_dependencies:
        del dep[name]
    pyproject_path.write_text(tomlkit.dumps(pyproject))
    subprocess.call(["poetry", "update"])

    # make the actual change
    pyproject = tomlkit.parse(pyproject_path.read_text())
    dep = pyproject["tool"]["poetry"]["dependencies"]
    for name, req in changed_dependencies.items():
        if isinstance(req, dict):
            if list(req.keys()) == ["version"]:
                req = req["version"]
            else:
                new_req = tomlkit.inline_table()
                new_req.update(req)
                req = new_req

        dep[name] = req
    pyproject_path.write_text(tomlkit.dumps(pyproject))
    subprocess.call(["poetry", "update"])


@app.command()
def version():
    """Replace all path requirements with version requirements in pyproject.toml"""
    dependencies = get_dependencies()
    changed_dependencies = {}
    for name, req in dependencies.items():
        if isinstance(req, dict) and "path" in req and get_pyproject_path(pathlib.Path(req["path"])).exists():
            version_req = "^" + get_version(pathlib.Path(req["path"]))
            changed_dependencies[name] = dependencies[name].copy()
            del changed_dependencies[name]["path"]
            changed_dependencies[name]["version"] = req["version"] = version_req
            typer.echo(f"{name}: Changing path requirement ../{name} to version requirement {req['version']}")

    set_changed_dependencies(changed_dependencies)


@app.command()
def path(develop: bool = typer.Option(True, help="Install path dependencies in develop mode")):
    """
    Replace all version dependencies with a path dependency in pyproject.toml (when ../dep_name exists)
    """
    dependencies = get_dependencies()
    changed_dependencies = {}
    for name, req in dependencies.items():
        if isinstance(req, str):
            dependencies[name] = req = {"version": req}

        if "path" not in req and get_pyproject_path(pathlib.Path("..") / name).exists():
            changed_dependencies[name] = dependencies[name].copy()
            del changed_dependencies[name]["version"]
            changed_dependencies[name]["path"] = f"../{name}"
            changed_dependencies[name]["develop"] = develop
            typer.echo(f"{name}: Changing version requirement {req['version']} to path requirement../{name}")

    set_changed_dependencies(changed_dependencies)


if __name__ == "__main__":
    app()
