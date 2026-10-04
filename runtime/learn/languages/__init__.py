"""Language plugins.

Each plugin provides:
- run_tests(workdir) -> list[CheckResult]: run a module copy's tests
- run_snippet(code) -> subprocess.CompletedProcess: run code on its own
"""

from ..course import CourseError
from . import python

PLUGINS = {"python": python}


def get(name):
    if name not in PLUGINS:
        raise CourseError(
            f"Language {name!r} is not supported. Supported: {', '.join(sorted(PLUGINS))}."
        )
    return PLUGINS[name]
