"""Tests for exercise/healthcheck.sh.

exercise/notfound.sh, exercise/count.sh and exercise/countall.sh are the
finished tools of modules 1 to 3, carried over unchanged, so they have no
tests here.
"""

import pytest

from checks import check_files_unchanged, log
from helpers import check, lines, run_script

HEALTHCHECK = "exercise/healthcheck.sh"
USAGE = "usage: healthcheck.sh LOGFILE"

# The requests of the example in healthcheck.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"  # 512 as the bytes
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024"  # 503 in the path
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"

# More requests.
LOGIN = "2026-10-06T10:17:20 203.0.113.5 POST /login 401 64"
MOVED = "2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 0"
GATEWAY = "2026-10-06T10:18:02 198.51.100.7 GET /api/users 502 0"
SLOW = "2026-10-06T10:18:30 192.0.2.44 GET /api/report 504 0"
ODD = "2026-10-06T10:18:55 203.0.113.5 GET /api/odd 599 0"
STATUS_PAGE = "2026-10-06T10:19:10 203.0.113.5 GET /status/503 200 64"  # path ends in 503
VIDEO = "2026-10-06T10:19:40 198.51.100.7 GET /video.mp4 200 5120"  # bytes start with 512
GONE = "2026-10-06T10:20:05 192.0.2.44 GET /gone.html 404 500"  # 500 as the bytes

ACCESS = log(INDEX, MISSING, STATS, ERROR_PAGE, UPLOAD)  # 5xx: STATS, UPLOAD
MONDAY = log(MONDAY_INDEX, OLD_PAGE)  # no 5xx
EXAMPLE = {"access.log": ACCESS, "monday log.log": MONDAY, "logs/monday.log": MONDAY}

PRINT_HINT = ('Print every line that contains " 5[0-9][0-9] ", as grep prints it, and only '
              "those lines.")
PATTERN_HINT = ('A request failed with a server error when its line contains " 5[0-9][0-9] ", '
                "with a space on each side, so a 5xx number in the path or the bytes doesn't "
                "count.")
STOP_HINT = "Stop once the requests are printed: exit 1 ends the script there."
TWICE_HINT = ("grep -q prints nothing, so it fits as the if condition; then print the requests "
              "once, with grep without -q.")
NO_ERRORS_HINT = ('When LOGFILE holds no 5xx request, print "LOGFILE: no 5xx errors", with '
                  "LOGFILE exactly as given.")
EMPTY_HINT = "An empty LOGFILE is still a regular file, with no 5xx request in it."
FOUND_STATUS_HINT = "Exit with status 1 when LOGFILE holds a 5xx request."
CLEAN_STATUS_HINT = ("Exit with status 0 when LOGFILE holds no 5xx request. A script without "
                     "exit ends with the status of its last command: make sure that is not a "
                     "grep or test that failed.")
SPACES_HINT = ('Put $1 in double quotes wherever you use it outside [[ ]]: "$1" keeps a name '
               "with spaces in one piece, its runs of spaces too.")
GLOB_HINT = ('Quoted, "$1" is plain text. Unquoted, a name with * ? or [ ] is a glob, and bash '
             "replaces it with the names of other files.")
STDERR_HINT = "Send the message to stderr: add >&2 at the end of the echo line."
STATUS_2_HINT = "Exit with status 2 right after the message."
GOES_ON_HINT = ("End the script with exit 2 right after the message: without exit, it "
                "goes on to the next steps.")
NO_ARGUMENT_HINT = ("Check $#, the number of arguments, before anything else: with none, print "
                    "the usage message to stderr and exit with 2.")
TWO_ARGUMENTS_HINT = ("Check $#, the number of arguments: unless it is exactly 1, print the usage "
                      "message, even when the first argument is a log file.")
ORDER_HINT = ("Check the number of arguments first, then the file: with two arguments, the "
              "usage message comes even when the first one is not a file.")
NO_FILE_HINT = ("Check with [[ ]] that LOGFILE is a regular file before grep reads it: when it "
                "isn't, print the message to stderr and exit with 2.")
FOLDER_HINT = "A folder is not a regular file: -e is true for a folder, -f is not."

# What bash and grep print to stderr when a name with spaces or glob
# characters is split, or replaced with other names.
NAME_ERRORS = ["No such file", "too many arguments", "operator expected", "ambiguous redirect"]


def healthcheck(*args, files):
    return run_script(HEALTHCHECK, *args, files=files)


def name_error(run):
    return any(error in run.stderr for error in NAME_ERRORS)


def check_errors_found(run, name, requests, hint):
    """Fail unless the run printed just `requests`, nothing to stderr, exited
    with 1 and left the files as they were."""
    expected = lines(log(*requests))
    if lines(run.stdout) == expected + [f"{name}: no 5xx errors"]:
        hint = STOP_HINT
    elif lines(run.stdout) == expected * 2:
        hint = TWICE_HINT
    elif name_error(run) and hint not in (SPACES_HINT, GLOB_HINT):
        hint = SPACES_HINT
    check(run, stdout=log(*requests), status=run.status, hint=hint)
    check(run, stderr="", status=run.status, hint=SPACES_HINT if name_error(run) else None)
    check(run, status=1, hint=FOUND_STATUS_HINT)
    check_files_unchanged(run)


def check_no_errors(run, name, hint):
    """Fail unless the run printed just "NAME: no 5xx errors", nothing to
    stderr, exited with 0 and left the files as they were."""
    printed = lines(run.stdout)
    if name_error(run) and hint not in (SPACES_HINT, GLOB_HINT):
        hint = SPACES_HINT
    elif hint is None and printed and all(line in lines(run.given[name]) for line in printed):
        hint = PATTERN_HINT
    elif hint is None:
        hint = NO_ERRORS_HINT
    check(run, stdout=f"{name}: no 5xx errors", status=run.status, hint=hint)
    check(run, stderr="", status=run.status, hint=SPACES_HINT if name_error(run) else None)
    check(run, status=0, hint=CLEAN_STATUS_HINT)
    check_files_unchanged(run)


def check_usage(run, hint):
    """Fail unless the run printed just the usage message to stderr, exited
    with 2 and left the files as they were."""
    if USAGE in lines(run.stdout):
        hint = STDERR_HINT
    elif USAGE in lines(run.stderr):
        hint = GOES_ON_HINT
    check(run, stdout="", stderr=USAGE, status=run.status, hint=hint)
    check(run, status=2, hint=STATUS_2_HINT)
    check_files_unchanged(run)


def check_no_such_file(run, name, hint):
    """Fail unless the run printed just the "no such file" message to stderr,
    exited with 2 and left the files as they were."""
    message = f"healthcheck.sh: no such file: {name}"
    if message in lines(run.stdout):
        hint = STDERR_HINT
    elif message in lines(run.stderr):
        hint = GOES_ON_HINT
    check(run, stdout="", stderr=message, status=run.status, hint=hint)
    check(run, status=2, hint=STATUS_2_HINT)
    check_files_unchanged(run)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "files, requests",
    [
        (EXAMPLE, [STATS, UPLOAD]),
        ({"access.log": log(UPLOAD, INDEX, GATEWAY, MISSING, STATS, LOGIN, SLOW, MOVED, ODD)},
         [UPLOAD, GATEWAY, STATS, SLOW, ODD]),
        ({"access.log": log(INDEX, MISSING, GATEWAY, LOGIN)}, [GATEWAY]),
        ({"access.log": log(STATS)}, [STATS]),
    ],
    ids=["example", "every-5xx-status", "one-among-others", "only-line"],
)
def test_prints_the_5xx_requests_and_exits_with_1(files, requests):
    check_errors_found(healthcheck("access.log", files=files), "access.log", requests,
                       PRINT_HINT)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "name, files, hint",
    [
        ("monday log.log", EXAMPLE, None),
        ("quiet.log", {"quiet.log": log(INDEX, MISSING, LOGIN, MOVED, OLD_PAGE)}, None),
        ("empty.log", {"empty.log": "", "access.log": ACCESS}, EMPTY_HINT),
        ("logs/monday.log", EXAMPLE, None),
    ],
    ids=["example", "4xx-and-others", "empty-log", "in-a-subfolder"],
)
def test_says_no_5xx_errors_and_exits_with_0(name, files, hint):
    check_no_errors(healthcheck(name, files=files), name, hint)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "requests, found",
    [
        ([INDEX, ERROR_PAGE, STATUS_PAGE, STATS, VIDEO, GONE], [STATS]),
        ([INDEX, ERROR_PAGE, STATUS_PAGE, VIDEO, GONE, MISSING], None),
    ],
    ids=["among-a-5xx-request", "without-a-5xx-request"],
)
def test_a_5xx_number_in_another_field_does_not_count(requests, found):
    run = healthcheck("access.log", files={"access.log": log(*requests)})
    if found:
        check_errors_found(run, "access.log", found, PATTERN_HINT)
    else:
        check_no_errors(run, "access.log", PATTERN_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "name, files, found, hint",
    [
        ("monday  log.log", {"monday  log.log": log(MONDAY_INDEX, STATS)}, [STATS], SPACES_HINT),
        ("  tuesday   log.log",
         {"  tuesday   log.log": MONDAY, "tuesday": ACCESS, "log.log": ACCESS}, None,
         SPACES_HINT),
        (" access.log", {" access.log": MONDAY, "access.log": ACCESS}, None, SPACES_HINT),
        ("*.log", {"*.log": log(UPLOAD), "access.log": MONDAY}, [UPLOAD], GLOB_HINT),
        ("[old].log", {"[old].log": MONDAY, "o.log": log(STATS)}, None, GLOB_HINT),
        ("day?.log", {"day?.log": log(INDEX, GATEWAY), "day1.log": MONDAY}, [GATEWAY],
         GLOB_HINT),
        ("logs/tuesday [old].log", {"logs/tuesday [old].log": log(UPLOAD, MISSING)}, [UPLOAD],
         SPACES_HINT),
    ],
    ids=["two-spaces-in-a-row", "spaces-at-the-start-and-in-a-row", "leading-space", "star",
         "brackets", "question-mark", "space-and-brackets"],
)
def test_names_with_spaces_and_glob_characters(name, files, found, hint):
    run = healthcheck(name, files=files)
    if found:
        check_errors_found(run, name, found, hint)
    else:
        check_no_errors(run, name, hint)


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "args, hint",
    [
        ([], NO_ARGUMENT_HINT),
        (["access.log", "monday log.log"], TWO_ARGUMENTS_HINT),
        (["access.log", "monday log.log", "logs/monday.log"], TWO_ARGUMENTS_HINT),
        (["access.log", ""], TWO_ARGUMENTS_HINT),
        (["missing.log", "access.log"], ORDER_HINT),
    ],
    ids=["no-argument", "two-arguments", "three-arguments", "an-empty-second-argument",
         "two-arguments-the-first-missing"],
)
def test_prints_usage_without_exactly_one_argument(args, hint):
    check_usage(healthcheck(*args, files=EXAMPLE), hint)


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "name, files, hint",
    [
        ("missing.log", EXAMPLE, NO_FILE_HINT),
        ("logs/missing.log", EXAMPLE, NO_FILE_HINT),
        ("logs", EXAMPLE, FOLDER_HINT),
        ("monday  log.log", EXAMPLE, SPACES_HINT),
        (" access.log", EXAMPLE, SPACES_HINT),
        ("*.log", {"access.log": ACCESS}, GLOB_HINT),
    ],
    ids=["missing", "missing-in-a-subfolder", "a-folder", "two-spaces-in-a-row",
         "leading-space", "star"],
)
def test_says_no_such_file_unless_a_regular_file(name, files, hint):
    check_no_such_file(healthcheck(name, files=files), name, hint)
