"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py.

Some checks load a file with source and then run several commands in the
same shell, as a script that uses the file would: to see whether a function
changed its caller's variables, or ended the whole script.
"""

import shlex

import pytest

from helpers import call, check, fail, indent, lines

# Client IPs of the made-up logs, by letter.
IPS = {"A": "203.0.113.5", "B": "10.0.0.8", "C": "198.51.100.7", "D": "172.16.0.3",
       "E": "192.0.2.44"}
PATHS = ["/index.html", "/about.html", "/logo.png", "/api/stats", "/login", "/missing.html"]
STATUSES = [200, 200, 404, 200, 301, 500, 401]
SIZES = [512, 2048, 4096, 0, 153, 64]

# Variables the caller holds before a function is called, all set to
# CALLER_VALUE. A function must leave every one as it was.
CALLER_VARIABLES = ["logfile", "count", "status", "n", "file", "line", "ip", "total", "result"]
CALLER_VALUE = "mine"

# Variables bash sets by itself, which may appear after any command.
SHELL_VARIABLES = {"_", "OLDPWD", "PIPESTATUS", "FUNCNAME", "COLUMNS", "LINES"}

# What grep, cut, sort, bash and [ print to stderr when a file name with
# spaces is split, or a glob in it is expanded to several names.
NAME_ERRORS = ["No such file", "ambiguous redirect", "too many arguments",
               "binary operator expected", "unary operator expected"]


def split_name(run, *names):
    """True when one of `names` holds spaces or * ? [ ], and the run's
    stderr shows a name that was split or expanded."""
    special = any(set(" *?[]") & set(name) for name in names)
    return special and any(error in run.stderr for error in NAME_ERRORS)


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


def text(*printed):
    """The expected output: `printed`, one per line."""
    return "".join(f"{line}\n" for line in printed)


def request(position, ip):
    """The request on line `position` (from 0) of a made-up log, from `ip`."""
    seconds = 15 * 60 + 11 * position
    time = f"2026-10-06T10:{seconds // 60:02d}:{seconds % 60:02d}"
    method = "POST" if position % 5 == 3 else "GET"
    path, status, size = (PATHS[position % len(PATHS)], STATUSES[position % len(STATUSES)],
                          SIZES[position % len(SIZES)])
    return f"{time} {ip} {method} {path} {status} {size}"


def log_of(letters):
    """A log whose lines come from the IPs that `letters` name, in that order."""
    return log(*(request(position, IPS[letter]) for position, letter in enumerate(letters)))


def shown(name):
    """A file name as a message shows it: in quotes when it starts or ends
    with spaces, so they don't look like indentation."""
    return f"'{name}'" if name != name.strip() else name


def given_files(run, about=None):
    """The files the run started with, as the first lines of a message.
    `about` ({name: sentence}) describes a file instead of showing it."""
    about = about or {}
    if not run.given:
        return "In an empty folder, "
    parts = []
    for name in sorted(run.given):
        content = run.given[name]
        if name in about:
            parts.append(about[name])
        elif lines(content):
            parts.append(f"{shown(name)} held:\n{indent(content)}")
        else:
            parts.append(f"{shown(name)} was empty.")
    return "\n".join(parts) + "\n"


def in_shell(path, *commands, files=None, functions=()):
    """Load `path` with source, then run `commands`, one per line, in the
    same shell. Messages show the run as `source <path>; <commands>`.
    `functions` are the ones the commands call from `path`."""
    run = call(path, "eval", "\n".join(commands), files=files)
    for function in functions:
        if f"{function}: command not found" in run.stderr:
            pytest.fail(f"{path} has no function called {function}.", pytrace=False)
    run.command = "; ".join([f"source {path}", *commands])
    return run


def check_run(run, stdout=None, status=0, stderr="", hint=None, status_hint=None, about=None,
              problem=None):
    """Fail unless the run printed `stdout` and `stderr` (each only if
    given), exited with `status` and left the files as they were. Each
    message starts with the files the run was given. `problem` is a hint for
    a mistake the run itself shows; it wins over `hint` and `status_hint`."""
    intro = given_files(run, about)
    if stdout is not None:
        with_intro(intro, run, stdout=stdout, status=run.status, hint=problem or hint)
    if stderr is not None:
        with_intro(intro, run, stderr=stderr, status=run.status, hint=problem or hint)
    with_intro(intro, run, status=status, hint=problem or status_hint or hint)
    check_files_unchanged(run, intro)


def with_intro(intro, run, **expected):
    """check(), with `intro` before its message."""
    try:
        check(run, **expected)
    except pytest.fail.Exception as error:
        message = error.msg
    else:
        return
    pytest.fail(intro + message, pytrace=False)


def check_files_unchanged(run, intro=""):
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


def sections(output):
    """The parts of `output` that follow each "@@<key>" line, by key."""
    found, key = {}, None
    for line in lines(output):
        if line.startswith("@@"):
            key = line[2:]
            found[key] = []
        elif key is not None:
            found[key].append(line)
    return found


def dump(name):
    """Shell commands that print "@@<name>", then "=<value>" when the
    variable is set."""
    return (f'echo "@@{name}"; '
            f'if [ -n "${{{name}+set}}" ]; then printf "%s\\n" "=${name}"; fi')


def check_keeps_variables(path, function, *args, files=None):
    """Fail unless calling `function` with `args`, in a shell that loaded
    `path` with source and set CALLER_VARIABLES, leaves each of them as it
    was and sets no new variable."""
    call_line = shlex.join([function, *args])
    commands = [f"{name}={CALLER_VALUE}" for name in CALLER_VARIABLES]
    commands += ["__before=; __after=", "__before=$(compgen -v)", f"{call_line} > /dev/null",
                 "__after=$(compgen -v)", 'echo "@@names before"; echo "$__before"',
                 'echo "@@names after"; echo "$__after"']
    commands += [dump(name) for name in CALLER_VARIABLES]
    run = in_shell(path, *commands, files=files, functions=[function])
    found = sections(run.stdout)
    setup = " ".join(f"{name}={CALLER_VALUE}" for name in CALLER_VARIABLES)
    where = (f"After these commands, in one shell:\n{indent(text(f'source {path}', setup, call_line))}"
             "\n")
    if "names after" not in found:
        fail(f"{where}the shell should go on after {function}, but {function} ended it.",
             f"End {function} with return, or let it end after its last command: exit ends "
             "the whole shell or script that called it.")
    for name in CALLER_VARIABLES:
        held = "\n".join(found.get(name, []))
        if held == f"={CALLER_VALUE}":
            continue
        if not held:
            now = "it is no longer set."
        elif "\n" in held:
            now = f"it holds:\n{indent(held[1:])}"
        else:
            now = f'it holds "{held[1:]}".'
        fail(f'{where}{name} should still hold "{CALLER_VALUE}", but {now}',
             f"Declare {name} inside {function} with local {name}, before you set it: a "
             "variable a function sets without local is its caller's.")
    before = set(found.get("names before", []))
    new = sorted(name for name in set(found["names after"]) - before
                 if name not in SHELL_VARIABLES and not name.startswith("BASH_"))
    if new:
        which = "a new variable" if len(new) == 1 else "new variables"
        fail(f"{where}{function} should set no variable outside itself, but the shell now has "
             f"{which}: {', '.join(new)}.",
             f"Declare every variable {function} sets with local, such as local {new[0]}.")
