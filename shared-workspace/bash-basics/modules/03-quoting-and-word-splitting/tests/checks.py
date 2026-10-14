"""Checks shared by this module's challenge and exercise tests, on top of
the ones in helpers.py."""

from helpers import fail, indent, lines


def log(*entries):
    """The text of a log file holding `entries`, one per line."""
    return "".join(f"{entry}\n" for entry in entries)


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
