"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py."""

import pytest

from helpers import check, fail, indent, lines

# What bash and sed print to stderr when a file name with spaces is split.
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


def spaces_hint(name):
    return (f'Put $1 in double quotes wherever you use it: "$1" keeps {name!r} in one piece, '
            "its runs of spaces too.")


def glob_hint(name, other):
    return (f"Put $1 in double quotes wherever you use it: quoted, the * ? [ ] in {name!r} are "
            f"plain text. Unquoted, they make a glob that can match other files, such as "
            f"{other}.")


def shown(name):
    """A file name as a message shows it: in quotes when it starts or ends
    with spaces, so they don't look like indentation."""
    return f"'{name}'" if name != name.strip() else name


def shows_content(name):
    return name.endswith(".log") or name.endswith(".anon")


def given_files(run):
    """The files the run started with, as the first lines of a message: the
    contents of each .log and .anon file, then the names of the other files."""
    if not run.given:
        return "In an empty folder, "
    parts = []
    for name in sorted(run.given):
        if shows_content(name):
            content = run.given[name]
            parts.append(f"{shown(name)} held:\n{indent(content)}" if lines(content)
                         else f"{shown(name)} was empty.")
    others = [name for name in sorted(run.given) if not shows_content(name)]
    if others:
        intro = "There were also these files:" if parts else "The folder held only these files:"
        parts.append(intro + "\n" + "\n".join(f"    {shown(name)}" for name in others))
    return "\n".join(parts) + "\n"


def check_in_folder(run, stdout=None, status=0, stderr=None, hint=None):
    """Like check(), but the message starts with the files the run was given,
    so the learner sees what the script read."""
    try:
        check(run, stdout=stdout, status=status, stderr=stderr, hint=hint)
    except pytest.fail.Exception as error:
        message = error.msg
    else:
        return
    pytest.fail(given_files(run) + message, pytrace=False)


def check_files_unchanged(run, written=(), hint=None):
    """Fail unless the run left the folder's files as they were: none created,
    changed or removed. Files named in `written` may be created or changed;
    other checks look at them."""
    after = {name: content for name, content in run.files.items() if name not in written}
    before = {name: content for name, content in run.given.items() if name not in written}
    if after == before:
        return
    changes = []
    for name, content in after.items():
        if name not in before:
            changes.append(f"created {shown(name)}, holding:\n{indent(content)}"
                           if lines(content) else f"created an empty {shown(name)}.")
        elif content != before[name]:
            now = f"Now it holds:\n{indent(content)}" if lines(content) else "Now it is empty."
            if shows_content(name):  # the message already starts with what it held
                changes.append(f"changed {shown(name)}. {now}")
            else:
                held = (f"Before, it held:\n{indent(before[name])}" if lines(before[name])
                        else "Before, it was empty.")
                changes.append(f"changed {shown(name)}. {held}\n{now}")
    changes += [f"removed {shown(name)}." for name in before if name not in after]
    other = f" other than {' and '.join(shown(name) for name in written)}" if written else ""
    message = f"`{run.command}` should not create or change any file{other}, but it {changes[0]}"
    message += "".join(f"\nIt also {change}" for change in changes[1:])
    fail(given_files(run) + message, hint)


def check_written(run, name, expected, hint=None):
    """Fail unless the run left the file `name` holding `expected`; an empty
    `expected` means an empty file."""
    content = run.files.get(name)
    if content is not None and lines(content) == lines(expected):
        return
    if lines(expected):
        should = f"should write {shown(name)} holding:\n{indent(expected)}\n"
    else:
        should = f"should write an empty {shown(name)}, "
    if content is None:
        got = f"but there is no {shown(name)}."
    elif lines(content):
        got = f"but it holds:\n{indent(content)}"
    else:
        got = "but it is empty."
    fail(given_files(run) + f"`{run.command}` " + should + got, hint)
