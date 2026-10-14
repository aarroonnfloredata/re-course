"""Tests for exercise/count.sh.

exercise/notfound.sh is module 1's finished tool, carried over unchanged, so
it has no tests here.
"""

import pytest

from helpers import check, fail, indent, lines, run_script

COUNT = "exercise/count.sh"

# The requests of the example in count.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024"  # 404 in the path
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
EXAMPLE = [INDEX, MISSING, LOGIN, ABOUT, ERROR_PAGE, FAVICON]

# More requests.
STATUS_PAGE = "2026-10-06T10:18:05 203.0.113.5 GET /status/404 200 512"  # path ends in 404
LOGO = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 4040"  # bytes start with 404
GONE = "2026-10-06T10:18:52 192.0.2.44 GET /gone.html 404 200"  # 200 as the bytes
OLD_PAGE = "2026-10-06T10:19:12 203.0.113.5 GET /old/page.html 404 153"
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 153"
UPLOAD = "2026-10-06T10:20:31 192.0.2.44 POST /upload 500 0"

# From an earlier run of notfound.sh.
YESTERDAY = "2026-10-05T23:58:44 192.0.2.44 GET /old.html 404 153"

PATTERN_HINT = ('A request has status STATUS when its line contains " STATUS ", with a space '
                "on each side, so the status in the path or the bytes doesn't count.")
EXIT_HINT = "Exit with status 0, also when N is 0: a script ends with the status of its last command."


def log(*entries):
    return "".join(f"{entry}\n" for entry in entries)


def line(logfile, count, status):
    return f"{logfile}: {count} requests with status {status}"


def count(logfile, status, files):
    return run_script(COUNT, logfile, status, files=files)


def check_line(run, expected, hint=None):
    """Fail unless the run printed just the line `expected`, nothing to stderr,
    and exited with status 0. Each is checked on its own, so `hint` only comes
    with a wrong line."""
    check(run, stdout=expected, status=run.status, hint=hint)
    check(run, stderr="", status=run.status)
    check(run, hint=EXIT_HINT)


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


@pytest.mark.objective(2, 3)
@pytest.mark.parametrize("status, expected", [("404", 2), ("200", 3)])
def test_counts_the_requests_with_the_status(status, expected):
    run = count("access.log", status, {"access.log": log(*EXAMPLE)})
    check_line(run, line("access.log", expected, status),
               hint="LOGFILE is $1 and STATUS is $2. Keep the number of matching lines in a "
                    "variable with $( ), then print it in the line.")


@pytest.mark.objective(3)
def test_one_request_still_says_requests():
    run = count("access.log", "401", {"access.log": log(*EXAMPLE)})
    check_line(run, line("access.log", 1, "401"),
               hint='The line always says "requests", even when N is 1.')


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "requests, status",
    [(EXAMPLE, "500"), ([], "404")],
    ids=["no-request-with-the-status", "empty-log"],
)
def test_no_requests_with_the_status(requests, status):
    run = count("access.log", status, {"access.log": log(*requests)})
    check_line(run, line("access.log", 0, status),
               hint="With no matching request, N is 0: grep -c prints 0 then.")


@pytest.mark.objective(3)
def test_counts_more_than_three_requests():
    requests = [INDEX, MISSING, LOGIN, ABOUT, FAVICON, STATUS_PAGE, OLD_PAGE, ROBOTS, UPLOAD]
    requests += [f"2026-10-06T11:{minute:02}:00 203.0.113.5 GET /page{minute}.html 404 153"
                 for minute in range(10)]
    run = count("access.log", "404", {"access.log": log(*requests)})
    check_line(run, line("access.log", 14, "404"),
               hint="Count every matching line of LOGFILE, not only the first or last few.")


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "requests, status, expected",
    [
        ([MISSING, ABOUT, ERROR_PAGE, FAVICON, STATUS_PAGE, LOGO], "404", 2),
        ([INDEX, ABOUT, ERROR_PAGE, STATUS_PAGE, LOGO], "404", 0),
        ([INDEX, MISSING, LOGIN, STATUS_PAGE, GONE], "200", 2),
    ],
    ids=["404-also-in-other-fields", "404-only-in-other-fields", "200-as-the-bytes"],
)
def test_status_in_another_field_does_not_count(requests, status, expected):
    run = count("access.log", status, {"access.log": log(*requests)})
    check_line(run, line("access.log", expected, status), hint=PATTERN_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize("status", ["40", "20"])
def test_a_longer_status_does_not_count(status):
    run = count("access.log", status, {"access.log": log(*EXAMPLE)})
    check_line(run, line("access.log", 0, status),
               hint='A longer status that starts with STATUS doesn\'t count: " STATUS " needs '
                    "a space after STATUS too.")


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "logfile, files, expected",
    [
        ("logs/monday.log", {"logs/monday.log": log(*EXAMPLE)}, 2),
        ("monday.log", {"access.log": log(*EXAMPLE),
                        "monday.log": log(INDEX, MISSING, OLD_PAGE, ROBOTS)}, 3),
    ],
    ids=["in-a-subfolder", "next-to-access-log"],
)
def test_reads_the_log_file_given_as_the_first_argument(logfile, files, expected):
    run = count(logfile, "404", files)
    check_line(run, line(logfile, expected, "404"),
               hint="LOGFILE is the first argument, $1: read that file, and print $1 as it "
                    "was given.")


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "files",
    [
        {"access.log": log(*EXAMPLE)},
        {"access.log": log(*EXAMPLE), "notfound.log": log(YESTERDAY), "errors.txt": ""},
    ],
    ids=["only-access-log", "with-notfound-files"],
)
def test_creates_and_changes_no_file(files):
    run = count("access.log", "404", files)
    check_line(run, line("access.log", 2, "404"))
    check_files_unchanged(run, hint="$( ) keeps grep's output in a variable, so no file is needed.")
