"""Bash courses: tests are pytest files that run the learner's scripts with
bash, so they run like a Python course's. Snippets run with `bash -c`, and
ShellCheck gives advice on the learner's files.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from ..course import CourseError
from .python import run_tests, test_objectives  # the tests are pytest files

EXTENSION = ".sh"
TIMEOUT = 60  # seconds for a ShellCheck run

# A top-level function: `name() {` at the start of a line, closed by `}` at
# the start of a line. lang-bash asks for this form.
FUNCTION = re.compile(r"^(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{\s*$")
# A stub's body says so on stderr: echo "<unit> is not written yet." >&2
STUB = re.compile(r'^echo "\S+ is not written yet\." >&2$')


def run_snippet(code, timeout=10):
    with tempfile.TemporaryDirectory() as tmp:
        return subprocess.run(
            ["bash", "-c", code], cwd=tmp, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=timeout,
        )


def lint(folder, paths):
    """ShellCheck findings for the bash files among `paths` (relative to
    `folder`), as "path:line: message (link to the explanation)" lines."""
    paths = [path for path in paths if Path(path).suffix == EXTENSION]
    if not paths:
        return []
    command = shellcheck()
    if command is None:
        raise CourseError(
            "ShellCheck is not installed in the course environment. "
            "The course's pyproject.toml should list re-course-learn[bash]."
        )
    process = subprocess.run(
        [command, "--format=json1", "--shell=bash", *paths], cwd=folder,
        capture_output=True, text=True, timeout=TIMEOUT,
    )
    if process.returncode not in (0, 1):  # 1: findings
        raise CourseError(f"ShellCheck could not run: {process.stderr.strip()}")
    comments = sorted(json.loads(process.stdout)["comments"],
                      key=lambda comment: (comment["file"], comment["line"], comment["column"]))
    return [f"{comment['file']}:{comment['line']}: {comment['message']} "
            f"(https://www.shellcheck.net/wiki/SC{comment['code']})"
            for comment in comments]


def shellcheck():
    """ShellCheck from the course environment (shellcheck-py), else from PATH."""
    beside = Path(sys.executable).parent / "shellcheck"
    return str(beside) if beside.is_file() else shutil.which("shellcheck")


# Used by the generator's validator only (see learn/authoring.py).


def stubs(path):
    """Names of the units in a starter file that are still stubs: functions by
    name, the script itself by its file name."""
    path = Path(path)
    if path.suffix != EXTENSION:
        return []
    return [name for name, lines in units(path).items()
            if any(STUB.match(line) for line in lines)]


def changed_units(original, changed):
    """Names of the units that differ between two versions of a file. Comment
    lines, blank lines and indentation don't count."""
    if Path(original).suffix != EXTENSION:
        return []
    before, after = units(original), units(changed)
    return sorted(name for name in before.keys() | after.keys()
                  if before.get(name) != after.get(name))


def units(path):
    """Split a bash file into its top-level functions and the rest, which is
    the script itself and goes under the file name: {name: [lines]}."""
    path = Path(path)
    found = {path.name: []}
    current = path.name
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = FUNCTION.match(line)
        if current == path.name and match:
            current = match.group(1)
            found[current] = []
        found[current].append(stripped)
        if current != path.name and line.rstrip() == "}":
            current = path.name
    if not found[path.name]:
        del found[path.name]
    return found
