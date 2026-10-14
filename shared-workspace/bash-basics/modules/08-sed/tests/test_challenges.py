"""Checks for the inline challenges in lesson.md."""

import pytest

from checks import check_files_unchanged, check_in_folder, log, name_error, spaces_hint, text
from helpers import lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

NOTES = log("Look into the 404s.")
ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'
STATUS_HINT = ("A script ends with the status of its last command: make sed the last one, and "
               "leave out the stub's exit 1.")


def check_challenge(script, args, files, expected, hint, diagnose=None):
    """Run `script` with `args`, the log file's name first, in a folder
    holding `files`, and fail unless it printed just the `expected` lines,
    nothing to stderr, exited with 0 and left the files as they were.
    `diagnose(given, got, expected)` names a mistake the output shows; its
    hint wins over `hint`."""
    run = run_script(script, *args, files=files)
    if name_error(run):
        problem = spaces_hint(args[0])
    elif diagnose:
        problem = diagnose(lines(files[args[0]]), lines(run.stdout), expected)
    else:
        problem = None
    check_in_folder(run, stdout=text(*expected), status=run.status, hint=problem or hint)
    check_in_folder(run, stderr="", status=run.status, hint=problem)
    check_in_folder(run, status=0, hint=STATUS_HINT)
    check_files_unchanged(run)


# c1

# Requests from the example in c1.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
LOGIN = "2026-10-06T10:16:02 192.0.2.44 POST /login 401 64"

# More requests.
HEALTH = "2026-10-06T10:16:20 127.0.0.1 HEAD /health 200 0"
DELETE = "2026-10-06T10:16:48 203.0.113.5 DELETE /api/items/7 204 0"
REPORT = "2026-10-06T10:17:03 198.51.100.7 GET /reports/2026-10-06.html 200 1024"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_LOGO = "2026-10-05T09:13:02 203.0.113.5 GET /logo.png 200 4096"


def csv(*requests):
    """`requests` as c1 prints them: every space replaced by a comma."""
    return [request.replace(" ", ",") for request in requests]


C1_HINT = "Replace every space with a comma: s/ /,/ with the g flag after the last slash."
C1_G_HINT = ("s replaces only the first match on each line: add the g flag after the last "
             "slash, so every space becomes a comma.")
C1_COMMA_HINT = "Replace each space with a comma alone, with no space after it."


def c1_mistake(given, got, expected):
    if got != expected and got == [line.replace(" ", ",", 1) for line in given]:
        return C1_G_HINT
    if any(", " in line for line in got):
        return C1_COMMA_HINT
    return None


@pytest.mark.objective(1)
def test_c1_prints_the_log_as_csv():
    check_challenge(C1, ["access.log"],
                    {"access.log": log(INDEX, MISSING, LOGIN), "notes.txt": NOTES},
                    csv(INDEX, MISSING, LOGIN), C1_HINT, c1_mistake)
    check_challenge(C1, ["access.log"],
                    {"access.log": log(HEALTH, REPORT, DELETE, INDEX)},
                    csv(HEALTH, REPORT, DELETE, INDEX), C1_HINT, c1_mistake)
    check_challenge(C1, ["access.log"], {"access.log": log(LOGIN)}, csv(LOGIN), C1_HINT,
                    c1_mistake)
    check_challenge(C1, ["empty.log"], {"empty.log": "", "access.log": log(INDEX, MISSING)}, [],
                    ARGUMENT_HINT)
    check_challenge(C1, ["monday.log"],
                    {"monday.log": log(MONDAY_INDEX, MONDAY_LOGO), "access.log": log(INDEX)},
                    csv(MONDAY_INDEX, MONDAY_LOGO), ARGUMENT_HINT, c1_mistake)
    check_challenge(C1, ["monday  log.log"], {"monday  log.log": log(MONDAY_LOGO, MONDAY_INDEX)},
                    csv(MONDAY_LOGO, MONDAY_INDEX), spaces_hint("monday  log.log"), c1_mistake)
    check_challenge(C1, ["  tuesday   log.log"], {"  tuesday   log.log": log(DELETE)},
                    csv(DELETE), spaces_hint("  tuesday   log.log"), c1_mistake)


# c2

# Requests from the example in c2.sh.
ERROR_PAGE = "2026-10-06T10:16:20 203.0.113.5 GET /errors/500.html 200 1024"

# More requests: paths with digits, dots and slashes, bytes that look like a
# status, and other methods.
GEO = "2026-10-06T10:16:48 192.0.2.44 GET /geo/192.0.2.44 200 404"
OLD_ERROR = "2026-10-06T10:17:03 198.51.100.7 HEAD /errors/404.html 301 0"
ITEM = "2026-10-06T10:17:30 203.0.113.5 DELETE /api/v1.2/items/500 204 0"
UPLOAD = "2026-10-06T10:18:02 192.0.2.44 PUT /files/2026/10/06/report.txt 201 2048"
NUMBERS = "2026-10-06T10:18:30 198.51.100.7 GET /x/200/y 500 200"
ROOT = "2026-10-06T10:18:55 127.0.0.1 GET / 200 2"


def status_and_path(*requests):
    """`requests` as c2 prints them: the status, a space and the path."""
    return [f"{request.split(' ')[4]} {request.split(' ')[3]}" for request in requests]


C2_HINT = ("Match the whole line, from ^ to $, one field at a time with [^ ]+, and put ( ) "
           "around the path and around the status. Then write the status's group, a space and "
           "the path's group.")
C2_ORDER_HINT = ("Print the status first, then the path: in the replacement, write the number of "
                 "the status's group first.")
C2_WHOLE_LINE_HINT = ("Match the whole line, from ^ to $: the text the pattern doesn't match "
                      "stays in the line.")
C2_FIELDS_HINT = ("Find the path and the status by their place, the 4th and 5th fields: digits "
                  "in the path or the bytes can look like a status, and a path can hold "
                  "several slashes.")
C2_ROOT_HINT = "A path can be just /: match each field with [^ ]+, whatever it holds."


def c2_mistake(given, got, expected):
    if got and got == [" ".join(reversed(line.split(" "))) for line in expected]:
        return C2_ORDER_HINT
    if any(len(line.split(" ")) > 2 for line in got):
        return C2_WHOLE_LINE_HINT
    return None


@pytest.mark.objective(2)
def test_c2_prints_the_status_and_path_of_each_request():
    check_challenge(C2, ["access.log"],
                    {"access.log": log(INDEX, MISSING, LOGIN, ERROR_PAGE), "notes.txt": NOTES},
                    status_and_path(INDEX, MISSING, LOGIN, ERROR_PAGE), C2_HINT, c2_mistake)
    check_challenge(C2, ["access.log"],
                    {"access.log": log(GEO, OLD_ERROR, ITEM, UPLOAD, NUMBERS)},
                    status_and_path(GEO, OLD_ERROR, ITEM, UPLOAD, NUMBERS), C2_FIELDS_HINT,
                    c2_mistake)
    check_challenge(C2, ["access.log"], {"access.log": log(ROOT, HEALTH)},
                    status_and_path(ROOT, HEALTH), C2_ROOT_HINT, c2_mistake)
    check_challenge(C2, ["empty.log"], {"empty.log": "", "access.log": log(INDEX, MISSING)}, [],
                    ARGUMENT_HINT)
    check_challenge(C2, ["monday.log"],
                    {"monday.log": log(MONDAY_LOGO, MONDAY_INDEX), "access.log": log(MISSING)},
                    status_and_path(MONDAY_LOGO, MONDAY_INDEX), ARGUMENT_HINT, c2_mistake)
    check_challenge(C2, ["monday  log.log"], {"monday  log.log": log(MONDAY_INDEX, DELETE)},
                    status_and_path(MONDAY_INDEX, DELETE), spaces_hint("monday  log.log"),
                    c2_mistake)
    check_challenge(C2, ["  tuesday   log.log"], {"  tuesday   log.log": log(LOGIN)},
                    status_and_path(LOGIN), spaces_hint("  tuesday   log.log"), c2_mistake)


# c3

# The five requests from the example in c3.sh.
FIVE = [
    "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
    "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    "2026-10-06T10:16:02 192.0.2.44 POST /login 401 64",
    "2026-10-06T10:16:20 127.0.0.1 GET /health 200 2",
    "2026-10-06T10:16:48 203.0.113.5 GET /about.html 200 2048",
]

# Twelve requests, for line numbers of two digits.
TWELVE = [f"2026-10-06T11:{minute:02d}:00 192.0.2.{minute} GET /page/{minute}.html 200 {minute}"
          for minute in range(1, 13)]


def lines_between(requests, first, last):
    """Lines `first` to `last` of `requests`, both included, counting from 1."""
    return requests[first - 1:last]


C3_HINT = ('Give sed -n, then the address FIRST,LAST and the p command, in double quotes so '
           'bash puts the numbers in: "$2,$3p". Lines FIRST and LAST are both printed. With '
           "variables, write ${last}p with braces: $lastp is a variable called lastp.")
C3_N_HINT = ("Give sed -n: without it, sed prints every line, and p prints the chosen ones a "
             "second time.")
C3_PAST_THE_END_HINT = ("When LOGFILE has fewer than LAST lines, print from line FIRST to its "
                        "last line; when it has fewer than FIRST lines, print nothing.")


def c3_mistake(given, got, expected):
    without_n = [copy for line in given for copy in [line] * (2 if line in expected else 1)]
    if given and got == without_n:
        return C3_N_HINT
    return None


def c3_check(name, first, last, requests, hint=C3_HINT, files=None):
    check_challenge(C3, [name, str(first), str(last)], {name: log(*requests), **(files or {})},
                    lines_between(requests, first, last), hint, c3_mistake)


@pytest.mark.objective(3)
def test_c3_prints_lines_first_to_last():
    c3_check("access.log", 2, 4, FIVE, files={"notes.txt": NOTES})
    c3_check("access.log", 3, 3, FIVE)
    c3_check("access.log", 1, 1, FIVE)
    c3_check("access.log", 5, 5, FIVE)
    c3_check("access.log", 1, 5, FIVE)
    c3_check("access.log", 4, 9, FIVE, C3_PAST_THE_END_HINT)
    c3_check("access.log", 6, 8, FIVE, C3_PAST_THE_END_HINT)
    c3_check("access.log", 10, 12, TWELVE)
    c3_check("access.log", 2, 11, TWELVE)
    c3_check("access.log", 9, 10, TWELVE)
    c3_check("empty.log", 1, 3, [], ARGUMENT_HINT, files={"access.log": log(*FIVE)})
    c3_check("monday.log", 1, 2, TWELVE[:4], ARGUMENT_HINT, files={"access.log": log(*FIVE)})
    c3_check("monday  log.log", 2, 3, FIVE[1:], spaces_hint("monday  log.log"))
    c3_check("  tuesday   log.log", 1, 1, FIVE[2:], spaces_hint("  tuesday   log.log"))
