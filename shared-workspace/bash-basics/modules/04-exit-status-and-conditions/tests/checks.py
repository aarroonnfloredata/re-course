"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py."""

from helpers import check_file, fail, indent, lines


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


def check_files_unchanged(run, hint=None, written=()):
    """Fail unless the run left the folder's files as they were: none created,
    changed or removed. Files named in `written` may be created or changed;
    other checks look at them."""
    after = {name: text for name, text in run.files.items() if name not in written}
    before = {name: text for name, text in run.given.items() if name not in written}
    if after == before:
        return
    changes = []
    for name, text in after.items():
        if name not in before:
            changes.append(f"created {name}, holding:\n{indent(text)}" if lines(text)
                           else f"created an empty {name}.")
        elif text != before[name]:
            held = (f"Before, it held:\n{indent(before[name])}" if lines(before[name])
                    else "Before, it was empty.")
            now = f"Now it holds:\n{indent(text)}" if lines(text) else "Now it is empty."
            changes.append(f"changed {name}. {held}\n{now}")
    changes += [f"removed {name}." for name in before if name not in after]
    other = f" other than {' and '.join(written)}" if written else ""
    message = f"`{run.command}` should not create or change any file{other}, but it {changes[0]}"
    message += "".join(f"\nIt also {change}" for change in changes[1:])
    fail(message, hint)


def check_file_holds(run, name, expected, hint=None):
    """Like check_file, but says "should be empty" when `expected` is empty."""
    if lines(expected):
        check_file(run, name, expected, hint)
        return
    if name in run.files and not run.files[name]:
        return
    message = ""
    if name in run.given:
        message = (f"{name} held:\n{indent(run.given[name])}\n" if lines(run.given[name])
                   else f"{name} was empty.\n")
    message += f"After `{run.command}`, {name} should be empty, "
    if name not in run.files:
        message += f"but there is no {name}."
    else:
        message += f"but it holds:\n{indent(run.files[name])}"
    fail(message, hint)
