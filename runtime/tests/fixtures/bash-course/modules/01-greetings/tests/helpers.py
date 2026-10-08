"""Helpers shared by this module's tests.

They run the learner's bash scripts and functions, each in a new empty
folder, and turn every failure into a plain-language message: what was run,
what was expected, what came back, and an optional hint. Output is compared
line by line, so a missing final newline doesn't count.
"""

import shlex
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent
TIMEOUT = 10  # seconds per run
NOT_WRITTEN = " is not written yet."  # what a stub prints to stderr
LOAD_FAILED = "learn: could not load the file"


@dataclass
class Run:
    """What a script or function did."""

    command: str  # as the learner would type it, e.g. "bash exercise/greet.sh Ada"
    stdin: str
    stdout: str
    stderr: str
    status: int
    given: dict = field(default_factory=dict)  # files in the folder before: {name: text}
    files: dict = field(default_factory=dict)  # files in the folder after: {name: text}


def run_script(path, *args, stdin="", files=None):
    """Run a learner script as `bash <path> <args>`, in a new folder holding
    `files` ({name: text}), with `stdin` as its input."""
    command = ["bash", str(MODULE_DIR / path), *args]
    return execute(command, shlex.join(["bash", path, *args]), stdin, files)


def call(path, function, *args, stdin="", files=None):
    """Load a learner file with `source` and call one of its functions with
    `args`, in a new folder holding `files`, with `stdin` as its input."""
    script = f'source "$1" || {{ echo "{LOAD_FAILED}" >&2; exit 1; }}; shift; "$@"'
    command = ["bash", "-c", script, "bash", str(MODULE_DIR / path), function, *args]
    run = execute(command, shlex.join([function, *args]), stdin, files)
    if LOAD_FAILED in run.stderr:
        error = run.stderr.replace(LOAD_FAILED, "").strip()
        pytest.fail(f"{path} could not be loaded:\n{indent(error)}", pytrace=False)
    if run.status == 127 and f"{function}: command not found" in run.stderr:
        pytest.fail(f"{path} has no function called {function}.", pytrace=False)
    return run


def execute(command, shown, stdin, files):
    given = dict(files or {})
    with tempfile.TemporaryDirectory(prefix="learn-run-") as tmp:
        folder = Path(tmp)
        for name, text in given.items():
            (folder / name).parent.mkdir(parents=True, exist_ok=True)
            (folder / name).write_text(text)
        try:
            process = subprocess.run(command, cwd=folder, input=stdin, capture_output=True,
                                     text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            pytest.fail(f"`{shown}` didn't finish within {TIMEOUT} seconds. Check for a "
                        "loop that never ends, or a command waiting for input.", pytrace=False)
        after = {path.relative_to(folder).as_posix(): path.read_text(errors="replace")
                 for path in sorted(folder.rglob("*")) if path.is_file()}
    stderr = process.stderr.replace(f"{MODULE_DIR}/", "")
    for line in stderr.splitlines():
        if line.endswith(NOT_WRITTEN):
            pytest.fail(line, pytrace=False)
    return Run(shown, stdin, process.stdout, stderr, process.returncode, given, after)


def check(run, stdout=None, status=0, stderr=None, hint=None):
    """Fail with a plain-language message unless the run printed `stdout` and
    `stderr` (each only if given) and exited with `status`."""
    if stdout is not None and lines(run.stdout) != lines(stdout):
        message = subject(run) + compare("print", stdout, run.stdout)
    elif stderr is not None and lines(run.stderr) != lines(stderr):
        message = subject(run) + compare("print", stderr, run.stderr, " to stderr")
    elif run.status != status:
        message = subject(run) + f"should exit with status {status}, but exited with {run.status}."
    else:
        return
    if run.stderr and stderr is None:
        message += f"\nIt printed this to stderr:\n{indent(run.stderr)}"
    fail(message, hint)


def check_file(run, name, expected, hint=None):
    """Fail with a plain-language message unless the run left the file `name`
    holding `expected`."""
    if name in run.files and lines(run.files[name]) == lines(expected):
        return
    message = ""
    if name in run.given:
        message = f"{name} held:\n{indent(run.given[name])}\n"
    message += f"After `{run.command}`, {name} should hold:\n{indent(expected)}\n"
    if name not in run.files:
        message += f"but there is no {name}."
    elif run.files[name]:
        message += f"but it holds:\n{indent(run.files[name])}"
    else:
        message += "but it is empty."
    fail(message, hint)


def subject(run):
    """How a message names the run: the command, and its input if it had any."""
    if run.stdin:
        return f"`{run.command}` with this input:\n{indent(run.stdin)}\n"
    return f"`{run.command}` "


def compare(verb, expected, actual, where=""):
    if lines(expected):
        should = f"should {verb}{where}:\n{indent(expected)}\n"
    else:
        should = f"should {verb} nothing{where}, "
    but = f"but printed:\n{indent(actual)}" if lines(actual) else "but printed nothing."
    return should + but


def fail(message, hint):
    if hint:
        message += f"\nHint: {hint}"
    pytest.fail(message, pytrace=False)


def lines(text):
    return text.splitlines()


def indent(text):
    return "\n".join(f"    {line}" for line in lines(text))
