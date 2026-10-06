"""Language plugins.

Each plugin provides, for learners:
- run_tests(workdir) -> list[CheckResult]: run a module copy's tests
- run_snippet(code) -> subprocess.CompletedProcess: run code on its own
- lint(folder, paths) -> ["path:line: message"] (optional): a linter's advice

and, for the generator's validator (see learn/authoring.py):
- EXTENSION: the file extension of the language's source files
- test_objectives(tests_dir) -> {"test_file::test_name": [objective numbers]}
- stubs(path) -> names of the units in a starter file that are still stubs
- changed_units(original, changed) -> names of the units that differ
"""

from ..course import CourseError
from . import bash, python

PLUGINS = {"bash": bash, "python": python}


def get(name):
    if name not in PLUGINS:
        raise CourseError(
            f"Language {name!r} is not supported. Supported: {', '.join(sorted(PLUGINS))}."
        )
    return PLUGINS[name]
