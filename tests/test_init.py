import pathlib
import poetry_dev

import pytest
import subprocess

from typer.testing import CliRunner

from poetry_dev import app

runner = CliRunner()


@pytest.mark.parametrize("spec", ["\"0.1.0\"", "{version = \"0.1.0\"}"])
def test_path(tmp_path: pathlib.Path, monkeypatch, spec: str):

    bar_pyproject_toml = tmp_path / "bar_pyproject_toml"
    bar_pyproject_toml.write_text(
        f"""[tool.poetry]
name = "bar"
version = "0.2.0"

[tool.poetry.dependencies]
python = "^3.7"
foo = {spec}

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
"""
    )

    foo_pyproject_toml = tmp_path / "foo_pyproject_toml"
    foo_pyproject_toml.write_text(
        """[tool.poetry]
name = "foo"
version = "0.2.0"

[tool.poetry.dependencies]
python = "^3.7"

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
"""
    )

    def get_pyproject_path(path=None):
        if "foo" in str(path):
            return foo_pyproject_toml
        return bar_pyproject_toml

    monkeypatch.setattr(poetry_dev, "get_pyproject_path", get_pyproject_path)
    monkeypatch.setattr(subprocess, "call", lambda _: None)

    result = runner.invoke(app, ["path"], catch_exceptions=False)
    assert result.exit_code == 0
    assert """foo = {path = "../foo", develop = true}""" in bar_pyproject_toml.read_text()


def test_version(tmp_path: pathlib.Path, monkeypatch):

    bar_pyproject_toml = tmp_path / "bar_pyproject_toml"
    bar_pyproject_toml.write_text(
        """[tool.poetry]
name = "bar"
version = "0.2.0"

[tool.poetry.dependencies]
python = "^3.7"
foo = {path = "../foo"}

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
"""
    )

    foo_pyproject_toml = tmp_path / "foo_pyproject_toml"
    foo_pyproject_toml.write_text(
        """[tool.poetry]
name = "foo"
version = "0.2.0"

[tool.poetry.dependencies]
python = "^3.7"

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
"""
    )

    def get_pyproject_path(path=None):
        if "foo" in str(path):
            return foo_pyproject_toml
        return bar_pyproject_toml

    monkeypatch.setattr(poetry_dev, "get_pyproject_path", get_pyproject_path)
    monkeypatch.setattr(subprocess, "call", lambda x: None)

    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert """foo = \"^0.2.0\"""" in bar_pyproject_toml.read_text()


def test_no_command():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "--help" in result.stdout
    assert "Commands" in result.stdout
