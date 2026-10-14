"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py.

The scripts here search a folder tree, so a failure message starts with the
files the run was given, and output that may come in any order is compared
without its order.
"""

import posixpath

from helpers import compare, fail, indent, lines, show, subject

# What find, grep, awk, xargs and bash print to stderr when a name is split
# at its spaces, or its quotes are taken as quotes.
NAME_ERRORS = ["No such file", "can't open file", "cannot open", "unterminated quote",
               "unmatched", "ambiguous redirect"]

# What find prints when an unquoted pattern expands to several names.
PATTERN_ERRORS = ["paths must precede expression", "unknown primary or operator"]

# A folder holding more files than this is shown in part.
MANY = 8


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


def text(*printed):
    """The expected output: `printed`, one per line."""
    return "".join(f"{line}\n" for line in printed)


def sized(size):
    """A file's text of exactly `size` bytes."""
    line = "." * 63 + "\n"
    return line * (size // 64) + "." * (size % 64)


def inside(folder, path):
    """True when `path`, a file's path from the run's folder, is under
    `folder`, also given from the run's folder."""
    return folder == "." or path.startswith(folder + "/")


def as_found(folder, path):
    """The file `path` as `find folder` prints it."""
    return f"./{path}" if folder == "." else path


def folders(files):
    """Every folder that holds one of `files`, as a path from the run's
    folder."""
    found = set()
    for path in files:
        parent = posixpath.dirname(path)
        while parent:
            found.add(parent)
            parent = posixpath.dirname(parent)
    return found


def name_error(run):
    """True when the run's stderr shows a name that was split, or whose
    quotes were taken as quotes."""
    return any(error in run.stderr for error in NAME_ERRORS)


def pattern_error(run):
    return any(error in run.stderr for error in PATTERN_ERRORS)


def shown(name):
    """A name as a message shows it: in quotes when it starts or ends with
    spaces, and as $'...' when it holds a newline."""
    if "\n" in name:
        escaped = name.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f"$'{escaped}'"
    if name != name.strip():
        quote = '"' if "'" in name else "'"
        return f"{quote}{name}{quote}"
    return name


def describe(given, contents):
    """The files a run started with, as the first lines of a message. With
    `contents`, each file's lines are shown, else its size."""
    if not given:
        return "In an empty folder, "
    by_folder = {}
    for path in sorted(given):
        by_folder.setdefault(posixpath.dirname(path), []).append(path)
    entries = []
    for path in sorted(given):
        siblings = by_folder[posixpath.dirname(path)]
        if len(siblings) > MANY and siblings.index(path) >= 3:
            if siblings.index(path) == 3:
                entries.append(f"    (and {len(siblings) - 3} more files in "
                               f"{shown(posixpath.dirname(path))})")
            continue
        content = given[path]
        if not contents:
            size = len(content.encode())
            entries.append(f"    {shown(path)}: {size} byte{'' if size == 1 else 's'}")
        elif not content:
            entries.append(f"    {shown(path)}: empty")
        else:
            held = "\n".join(f"        {show(line)}" for line in lines(content))
            entries.append(f"    {shown(path)}:\n{held}")
    return "In a folder holding these files:\n" + "\n".join(entries) + "\n"


def check_run(run, expected, contents=True, any_order=False, hint=None, problem=None):
    """Fail unless the run printed just the `expected` lines (in any order
    with `any_order`), nothing to stderr, exited with 0 and left the files as
    they were. `problem` is a hint for a mistake the run itself shows; it
    wins over `hint`."""
    intro = describe(run.given, contents)
    got = lines(run.stdout)
    if (sorted(got) != sorted(expected)) if any_order else (got != expected):
        where = ", in any order" if any_order and len(expected) > 1 else ""
        message = subject(run) + compare("print", text(*expected), run.stdout, where)
        if run.stderr:
            message += f"\nIt printed this to stderr:\n{indent(run.stderr)}"
        fail(intro + message, problem or hint)
    if lines(run.stderr):
        fail(intro + subject(run) + compare("print", "", run.stderr, " to stderr"), problem)
    if run.status != 0:
        fail(intro + subject(run) + f"should exit with status 0, but exited with {run.status}.",
             "A script ends with the status of its last command: make sure that one succeeds, "
             "and leave out the stub's exit 1.")
    check_files_unchanged(run, intro)


def check_files_unchanged(run, intro):
    """Fail unless the run left the folder's files as they were: none
    created, changed or removed."""
    if run.files == run.given:
        return
    changes = []
    for name, content in run.files.items():
        if name not in run.given:
            changes.append(f"created {shown(name)}, holding:\n{indent(content)}"
                           if lines(content) else f"created an empty {shown(name)}.")
        elif content != run.given[name]:
            now = f"Now it holds:\n{indent(content)}" if lines(content) else "Now it is empty."
            changes.append(f"changed {shown(name)}. {now}")
    changes += [f"removed {shown(name)}." for name in run.given if name not in run.files]
    message = f"`{run.command}` should not create or change any file, but it {changes[0]}"
    message += "".join(f"\nIt also {change}" for change in changes[1:])
    fail(intro + message, None)
