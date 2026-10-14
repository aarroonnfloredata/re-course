"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py."""

import pytest

from helpers import check, fail, indent, lines


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


def given_files(run):
    """The files the run started with, as the first lines of a message: the
    contents of each .log file, then the names of the other files."""
    if not run.given:
        return "In an empty folder, "
    parts = []
    for name in sorted(run.given):
        if name.endswith(".log"):
            text = run.given[name]
            parts.append(f"{name} held:\n{indent(text)}" if lines(text) else f"{name} was empty.")
    others = [name for name in sorted(run.given) if not name.endswith(".log")]
    if others:
        intro = "There were also these files:" if parts else "The folder held only these files:"
        parts.append(intro + "\n" + "\n".join(f"    {name}" for name in others))
    return "\n".join(parts) + "\n"


def check_in_folder(run, stdout=None, status=0, stderr=None, hint=None):
    """Like check(), but the message starts with the files the run was given,
    so the learner sees what the script read."""
    try:
        check(run, stdout=stdout, status=status, stderr=stderr, hint=hint)
    except pytest.fail.Exception as error:
        pytest.fail(given_files(run) + error.msg, pytrace=False)


def check_files_unchanged(run, hint=None):
    """Fail unless the run left the folder's files as they were: none created,
    changed or removed."""
    if run.files == run.given:
        return
    changes = []
    for name, text in run.files.items():
        if name not in run.given:
            changes.append(f"created {name}, holding:\n{indent(text)}" if lines(text)
                           else f"created an empty {name}.")
        elif text != run.given[name]:
            before = (f"Before, it held:\n{indent(run.given[name])}" if lines(run.given[name])
                      else "Before, it was empty.")
            after = f"Now it holds:\n{indent(text)}" if lines(text) else "Now it is empty."
            changes.append(f"changed {name}. {before}\n{after}")
    changes += [f"removed {name}." for name in run.given if name not in run.files]
    message = f"`{run.command}` should not create or change any file, but it {changes[0]}"
    message += "".join(f"\nIt also {change}" for change in changes[1:])
    fail(message, hint)
