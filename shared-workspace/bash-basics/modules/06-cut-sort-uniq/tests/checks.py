"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py."""

import pytest

from helpers import check, fail, indent, lines

# What bash and cut print to stderr when a file name with spaces is split.
NAME_ERRORS = ["No such file", "ambiguous redirect", "Is a directory"]


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


def text(*printed):
    """The expected output: `printed`, one per line."""
    return "".join(f"{line}\n" for line in printed)


def name_error(run):
    """True when the run's stderr shows a file name that was split."""
    return any(error in run.stderr for error in NAME_ERRORS)


def shown(name):
    """A file name as a message shows it: in quotes when it starts or ends
    with spaces, so they don't look like indentation."""
    return f"'{name}'" if name != name.strip() else name


def given_files(run, about=None):
    """The files the run started with, as the first lines of a message: the
    contents of each .log file, then the names of the other files. `about`
    ({name: sentence}) describes a long file instead of showing it."""
    about = about or {}
    if not run.given:
        return "In an empty folder, "
    parts = []
    for name in sorted(run.given):
        if name in about:
            parts.append(about[name])
        elif name.endswith(".log"):
            content = run.given[name]
            parts.append(f"{shown(name)} held:\n{indent(content)}" if lines(content)
                         else f"{shown(name)} was empty.")
    others = [name for name in sorted(run.given) if not name.endswith(".log")]
    if others:
        intro = "There were also these files:" if parts else "The folder held only these files:"
        parts.append(intro + "\n" + "\n".join(f"    {shown(name)}" for name in others))
    return "\n".join(parts) + "\n"


def check_in_folder(run, stdout=None, status=0, stderr=None, hint=None, about=None):
    """Like check(), but the message starts with the files the run was given,
    so the learner sees what the script read."""
    try:
        check(run, stdout=stdout, status=status, stderr=stderr, hint=hint)
    except pytest.fail.Exception as error:
        pytest.fail(given_files(run, about) + error.msg, pytrace=False)


def check_files_unchanged(run, hint=None):
    """Fail unless the run left the folder's files as they were: none created,
    changed or removed."""
    if run.files == run.given:
        return
    changes = []
    for name, content in run.files.items():
        if name not in run.given:
            changes.append(f"created {name}, holding:\n{indent(content)}" if lines(content)
                           else f"created an empty {name}.")
        elif content != run.given[name]:
            before = (f"Before, it held:\n{indent(run.given[name])}" if lines(run.given[name])
                      else "Before, it was empty.")
            after = f"Now it holds:\n{indent(content)}" if lines(content) else "Now it is empty."
            changes.append(f"changed {name}. {before}\n{after}")
    changes += [f"removed {name}." for name in run.given if name not in run.files]
    message = f"`{run.command}` should not create or change any file, but it {changes[0]}"
    message += "".join(f"\nIt also {change}" for change in changes[1:])
    fail(message, hint)


def check_run(run, expected, hint=None, problem=None, about=None):
    """Fail unless the run printed just the `expected` lines, nothing to
    stderr, exited with 0 and left the files as they were. `problem` is a
    hint for a mistake the run itself shows; it wins over `hint`."""
    check_in_folder(run, stdout=expected, status=run.status, hint=problem or hint, about=about)
    check_in_folder(run, stderr="", status=run.status, hint=problem, about=about)
    check_in_folder(run, status=0, about=about)
    check_files_unchanged(run)
