"""Tests for exercise/notfound.sh."""

import pytest

from helpers import check, check_file, fail, indent, lines, run_script

NOTFOUND = "exercise/notfound.sh"

# Requests in time order. The 404 requests have " 404 " in their line;
# the others hold 404 only in another field, or not at all.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
OLD_PAGE = "2026-10-06T10:16:02 203.0.113.5 GET /old/page.html 404 153"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024"  # 404 in the path
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
LOGIN = "2026-10-06T10:17:30 192.0.2.44 POST /login.php 404 153"
STATUS_PAGE = "2026-10-06T10:18:05 203.0.113.5 GET /status/404 200 512"  # path ends in 404
LOGO = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 4040"  # bytes start with 404
ROBOTS = "2026-10-06T10:19:12 203.0.113.5 GET /robots.txt 404 153"
ADMIN = "2026-10-06T10:19:40 198.51.100.7 GET /admin/ 404 153"

# From an earlier run.
YESTERDAY = "2026-10-05T23:58:44 192.0.2.44 GET /old.html 404 153"

EXAMPLE = [INDEX, MISSING, OLD_PAGE, ABOUT, ERROR_PAGE, FAVICON, LOGIN]
EVERYTHING = [INDEX, MISSING, OLD_PAGE, ABOUT, ERROR_PAGE, FAVICON, LOGIN,
              STATUS_PAGE, LOGO, ROBOTS, ADMIN]

PATTERN_HINT = ('A 404 request has " 404 " in its line, with a space on each side, '
                "so 404 in the path or the bytes doesn't count.")
TAIL_HINT = "Print the last lines of notfound.log, not of access.log: tail -n 3 notfound.log."
NO_ACCESS_LOG = " in a folder without access.log"


def log(*entries):
    return "".join(f"{entry}\n" for entry in entries)


def check_empty(run, name, where="", hint=None):
    """Fail unless the run left the file `name` in the folder, empty."""
    text = run.files.get(name)
    if text is not None and not lines(text):
        return
    message = ""
    if name in run.given:
        message = f"{name} held:\n{indent(run.given[name])}\n"
    message += f"After `{run.command}`{where}, {name} should be empty, "
    if text is None:
        message += f"but there is no {name}."
    else:
        message += f"but it holds:\n{indent(text)}"
    fail(message, hint)


def check_error_message(run, hint=None):
    """Fail unless errors.txt holds one line that names access.log."""
    text = run.files.get("errors.txt")
    if text is not None and len(lines(text)) == 1 and "access.log" in text:
        return
    message = ""
    if "errors.txt" in run.given:
        message = f"errors.txt held:\n{indent(run.given['errors.txt'])}\n"
    message += (f"After `{run.command}`{NO_ACCESS_LOG}, errors.txt should hold grep's "
                "error message: one line that names access.log,\n")
    if text is None:
        message += "but there is no errors.txt."
    elif lines(text):
        message += f"but it holds:\n{indent(text)}"
    else:
        message += "but it is empty."
    fail(message, hint)


@pytest.mark.objective(2, 4)
@pytest.mark.parametrize(
    "requests, found",
    [
        (EXAMPLE, [MISSING, OLD_PAGE, FAVICON, LOGIN]),
        ([INDEX, MISSING, ABOUT, ERROR_PAGE, STATUS_PAGE, LOGO, ROBOTS], [MISSING, ROBOTS]),
        (EVERYTHING, [MISSING, OLD_PAGE, FAVICON, LOGIN, ROBOTS, ADMIN]),
    ],
    ids=["example", "404-in-other-fields", "six-404-requests"],
)
def test_saves_the_404_requests(requests, found):
    run = run_script(NOTFOUND, files={"access.log": log(*requests)})
    check_file(run, "notfound.log", log(*found), hint=PATTERN_HINT)


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "requests, printed",
    [
        ([MISSING, ABOUT, ERROR_PAGE, STATUS_PAGE], [MISSING]),
        ([INDEX, MISSING, ABOUT, FAVICON, LOGO], [MISSING, FAVICON]),
        ([MISSING, OLD_PAGE, ERROR_PAGE, FAVICON, STATUS_PAGE], [MISSING, OLD_PAGE, FAVICON]),
        (EXAMPLE, [OLD_PAGE, FAVICON, LOGIN]),
        (EVERYTHING, [LOGIN, ROBOTS, ADMIN]),
    ],
    ids=["one", "two", "three", "four-example", "six"],
)
def test_prints_the_last_three_404_requests(requests, printed):
    run = run_script(NOTFOUND, files={"access.log": log(*requests)})
    check(run, stdout=log(*printed), stderr="", hint=TAIL_HINT)


@pytest.mark.objective(2, 4)
@pytest.mark.parametrize(
    "access",
    [log(INDEX, ABOUT, ERROR_PAGE, STATUS_PAGE, LOGO), ""],
    ids=["404-only-in-other-fields", "empty-access-log"],
)
def test_no_404_requests(access):
    run = run_script(NOTFOUND, files={"access.log": access})
    check(run, stdout="", stderr="", hint=PATTERN_HINT)
    check_empty(run, "notfound.log", hint="> notfound.log creates the file even when grep finds nothing.")
    check_empty(run, "errors.txt", hint="2> errors.txt on grep creates the file even when there is no error.")


@pytest.mark.objective(2)
def test_replaces_what_notfound_log_held():
    run = run_script(NOTFOUND, files={"access.log": log(INDEX, MISSING, OLD_PAGE),
                                      "notfound.log": log(YESTERDAY)})
    check_file(run, "notfound.log", log(MISSING, OLD_PAGE),
               hint="> replaces what a file held; >> adds to it.")
    check(run, stdout=log(MISSING, OLD_PAGE), stderr="")


@pytest.mark.objective(3)
def test_errors_txt_ends_up_empty_when_access_log_exists():
    run = run_script(NOTFOUND, files={"access.log": log(*EXAMPLE)})
    check_empty(run, "errors.txt",
                hint="2> errors.txt on grep creates the file even when there is no error.")

    run = run_script(NOTFOUND, files={"access.log": log(*EXAMPLE),
                                      "errors.txt": "error from an earlier run\n"})
    check_empty(run, "errors.txt",
                hint="2> errors.txt on grep replaces what errors.txt held; 2>> would add to it.")


@pytest.mark.objective(3)
def test_missing_access_log():
    run = run_script(NOTFOUND)
    check(run, stdout="", stderr="",
          hint="2> errors.txt on grep sends its error message to the file instead of the screen.")
    check_error_message(run, hint="2> errors.txt on grep sends its error message to the file.")
    check_empty(run, "notfound.log", where=NO_ACCESS_LOG,
                hint="> notfound.log creates the file even when grep finds nothing.")


@pytest.mark.objective(2, 3)
def test_missing_access_log_replaces_both_files():
    run = run_script(NOTFOUND, files={"notfound.log": log(YESTERDAY),
                                      "errors.txt": "error from an earlier run\n"})
    check_empty(run, "notfound.log", where=NO_ACCESS_LOG,
                hint="> notfound.log replaces what the file held, even when grep finds nothing.")
    check_error_message(run, hint="2> errors.txt on grep replaces what errors.txt held; "
                                  "2>> would add to it.")
    check(run, stdout="", stderr="")
