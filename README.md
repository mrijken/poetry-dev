# poetry-dev

![Build](https://github.com/mrijken/poetry-dev/workflows/CI/badge.svg)

When developing multiple Python packages concurrently with Poetry manageed environments you
can install the local package as path requirements. Ie when you develop `bar`
which have `foo` as dependency, which you also want to edit, you can
do `poetry add ../foo` from `bar` package. But when you want to publish
`bar`, you have to change the path requirement back to a version requirement.

After publishing `bar` you have to switch back to `foo` as a path requirement
in order to continue develop both concurrently.

This package will help you to improve that task. With one command all version
requirements will be changed to path requirements (when the package is
checkout in a sibling directory with the same as the package name).

`poetry_dev path`

This results in a changed `pyproject.toml` file. `poetry update` is called
to make sure the package on the path is installed as editable package.

Before publishing, the path requirements can be switched back to version
requirements with the following command.

`poetry_dev version`

The version of the dependency on the local path will be
used as minimal caret version in the changed `pyproject.toml` and
`poetry update` is called to make sure the corresponding version
from the repository will be installed.
