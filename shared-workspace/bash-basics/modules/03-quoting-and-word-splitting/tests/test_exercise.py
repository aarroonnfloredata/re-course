"""Tests for exercise/countall.sh.

exercise/notfound.sh and exercise/count.sh are the finished tools of modules 1
and 2, carried over unchanged, so they have no tests here.
"""

import pytest

from checks import check_files_unchanged, log
from helpers import check, run_script

COUNTALL = "exercise/countall.sh"

# The requests of the example in countall.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"
UPLOAD = "2026-10-04T18:20:31 192.0.2.44 POST /upload 500 0"

# More requests.
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024"  # 404 in the path
STATUS_PAGE = "2026-10-06T10:18:05 203.0.113.5 GET /status/404 200 512"  # path ends in 404
LOGO = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 4040"  # bytes start with 404
GONE = "2026-10-06T10:18:52 192.0.2.44 GET /gone.html 404 200"  # 200 as the bytes
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 153"

ACCESS = log(INDEX, MISSING, ABOUT, FAVICON)  # 404: 2, 200: 2, 401: 0, 500: 0
MONDAY = log(MONDAY_INDEX, OLD_PAGE)  # 404: 1, 200: 1, 401: 0, 500: 0
TUESDAY = log(UPLOAD)  # 404: 0, 200: 0, 401: 0, 500: 1
LOGS = {"access.log": ACCESS, "monday.log": MONDAY, "tuesday.log": TUESDAY}

STATUS_HINT = ('Count the lines that contain " STATUS ", with the value of STATUS in it: in '
               "double quotes $status expands, in single quotes it stays plain text.")
PATTERN_HINT = ('A request has status STATUS when its line contains " STATUS ", with a space '
                "on each side, so STATUS in the path or the bytes doesn't count.")
PASS_ON_HINT = ('After status=$1 and shift, "$@" holds every FILE, in the order given: pass it '
                "on to grep as it is.")
ONE_FILE_HINT = "Given one file, grep -c prints just the number; -H makes it print the name too."
SPACES_HINT = ('"$@" passes each FILE on as one argument, spaces and all. Unquoted $@ or $* '
               'splits the names at spaces, and "$*" joins them all into one.')
SPECIAL_HINT = ('In "$@" each name is plain text. Unquoted, a name with * ? or [ ] is a glob, '
                "and bash replaces it with the names of other files.")
NAMES_HINT = ('Every FILE exists, so "No such file" means grep got a wrong name: STATUS, which '
              'shift removes, or a FILE split into words or joined with others. "$@" passes '
              "each FILE on whole.")
EXIT_HINTS = {
    0: ("Exit with status 0 when at least one FILE holds a request with STATUS: that is the "
        "status of one grep over all the files."),
    1: ("Exit with status 1 when no FILE holds a request with STATUS: that is grep's own "
        "status, when grep is the script's last command."),
}


def countall(status, names, files):
    return run_script(COUNTALL, status, *names, files=files)


def counts(names, numbers):
    """What countall.sh prints: one NAME:N line for each file."""
    return "".join(f"{name}:{number}\n" for name, number in zip(names, numbers))


def check_counts(run, expected, status=0, hint=None):
    """Fail unless the run printed just `expected`, nothing to stderr, exited
    with `status` and left the files as they were. Whatever the test is about,
    a grep error about a missing file gets NAMES_HINT, and the right numbers
    without the names get ONE_FILE_HINT."""
    numbers_only = [line.rsplit(":", 1)[1] for line in expected.splitlines()]
    if "No such file" in run.stderr:
        hint = NAMES_HINT
    elif run.stdout.splitlines() == numbers_only:
        hint = ONE_FILE_HINT
    check(run, stdout=expected, status=run.status, hint=hint)
    check(run, stderr="", status=run.status, hint=hint if hint == NAMES_HINT else None)
    check(run, status=status, hint=EXIT_HINTS[status])
    check_files_unchanged(run)


@pytest.mark.objective(2, 3)
@pytest.mark.parametrize(
    "status, names, numbers",
    [
        ("404", ["access.log", "monday.log"], [2, 1]),
        ("200", ["access.log", "monday.log"], [2, 1]),
        ("500", ["access.log", "monday.log", "tuesday.log"], [0, 0, 1]),
    ],
)
def test_counts_the_status_in_each_file(status, names, numbers):
    check_counts(countall(status, names, LOGS), counts(names, numbers), hint=STATUS_HINT)


@pytest.mark.objective(5)
@pytest.mark.parametrize(
    "names, files, numbers",
    [
        (["monday.log", "access.log", "tuesday.log"], LOGS, [1, 2, 0]),
        (["access.log", "monday.log", "access.log"], LOGS, [2, 1, 2]),
        (["logs/monday.log", "access.log"], {"logs/monday.log": MONDAY, "access.log": ACCESS},
         [1, 2]),
    ],
    ids=["in-the-order-given", "a-file-given-twice", "in-a-subfolder"],
)
def test_passes_on_every_file_as_given(names, files, numbers):
    check_counts(countall("404", names, files), counts(names, numbers), hint=PASS_ON_HINT)


@pytest.mark.objective(5)
@pytest.mark.parametrize(
    "status, name, number",
    [("404", "access.log", 2), ("404", "logs/monday.log", 1), ("500", "tuesday.log", 1)],
)
def test_one_file_still_gets_its_name(status, name, number):
    files = {"access.log": ACCESS, "logs/monday.log": MONDAY, "tuesday.log": TUESDAY}
    check_counts(countall(status, [name], files), counts([name], [number]), hint=ONE_FILE_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "status, names, files, numbers",
    [
        ("404", ["access.log", "monday log.log"],
         {"access.log": ACCESS, "monday log.log": MONDAY}, [2, 1]),
        ("404", ["monday log.log"], {"access.log": ACCESS, "monday log.log": MONDAY}, [1]),
        ("404", ["monday  log.log", "access.log"],
         {"access.log": ACCESS, "monday  log.log": MONDAY}, [1, 2]),
        ("404", [" access.log"], {" access.log": MONDAY, "access.log": ACCESS}, [1]),
        ("404", ["  tuesday   log.log", "monday log.log"],
         {"  tuesday   log.log": log(MISSING, ROBOTS, FAVICON), "monday log.log": MONDAY,
          "tuesday": ACCESS, "log.log": MONDAY}, [3, 1]),
        ("500", ["access.log", "monday log.log", "logs/tuesday [old].log"],
         {"access.log": ACCESS, "monday log.log": MONDAY, "logs/tuesday [old].log": TUESDAY},
         [0, 0, 1]),
    ],
    ids=["one-space", "one-file-with-a-space", "two-spaces-in-a-row", "leading-space",
         "spaces-at-the-start-and-in-a-row", "space-and-brackets"],
)
def test_names_with_spaces(status, names, files, numbers):
    check_counts(countall(status, names, files), counts(names, numbers), hint=SPACES_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "names, files, numbers",
    [
        (["*.log"], {"*.log": log(MISSING, OLD_PAGE), "access.log": ACCESS, "monday.log": MONDAY},
         [2]),
        (["logs/[old].log"], {"logs/[old].log": log(MISSING), "logs/o.log": log(MISSING, FAVICON)},
         [1]),
        (["day?.log", "access.log"], {"day?.log": log(INDEX), "day1.log": log(MISSING),
                                      "access.log": ACCESS}, [0, 2]),
        (["$status.log", '"old".log'], {"$status.log": log(MISSING), '"old".log': MONDAY,
                                         "access.log": ACCESS}, [1, 1]),
    ],
    ids=["star", "brackets", "question-mark", "dollar-and-quotes"],
)
def test_names_with_special_characters(names, files, numbers):
    check_counts(countall("404", names, files), counts(names, numbers), hint=SPECIAL_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "status, access, monday, numbers",
    [
        ("404", [MISSING, ABOUT, ERROR_PAGE, FAVICON, STATUS_PAGE, LOGO],
         [INDEX, ERROR_PAGE, ABOUT, STATUS_PAGE, LOGO], [2, 0]),
        ("200", [INDEX, MISSING, GONE, STATUS_PAGE], [GONE, ROBOTS], [2, 0]),
    ],
    ids=["404-also-in-other-fields", "200-as-the-bytes"],
)
def test_status_in_another_field_does_not_count(status, access, monday, numbers):
    names = ["access.log", "monday.log"]
    run = countall(status, names, {"access.log": log(*access), "monday.log": log(*monday)})
    check_counts(run, counts(names, numbers), hint=PATTERN_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize("status", ["40", "20"])
def test_a_longer_status_does_not_count(status):
    names = ["access.log", "monday.log"]
    check_counts(countall(status, names, LOGS), counts(names, [0, 0]), status=1,
                 hint='A longer status that starts with STATUS doesn\'t count: " STATUS " needs '
                      "the space after STATUS too.")


@pytest.mark.objective(5)
@pytest.mark.parametrize(
    "status, names, files",
    [
        ("401", ["access.log", "monday log.log"], {"access.log": ACCESS, "monday log.log": MONDAY}),
        ("404", ["empty.log", "tuesday.log"], {"empty.log": "", "tuesday.log": TUESDAY}),
    ],
    ids=["no-request-with-the-status", "an-empty-file"],
)
def test_exits_with_1_when_no_file_has_the_status(status, names, files):
    check_counts(countall(status, names, files), counts(names, [0] * len(names)), status=1,
                 hint="N can be 0: grep -c prints 0 for a file without a matching line.")


@pytest.mark.objective(5)
@pytest.mark.parametrize(
    "status, names, numbers",
    [
        ("404", ["access.log", "tuesday.log"], [2, 0]),
        ("500", ["access.log", "tuesday.log", "monday.log"], [0, 1, 0]),
    ],
    ids=["only-the-first-file", "only-the-middle-file"],
)
def test_exits_with_0_when_any_file_has_the_status(status, names, numbers):
    check_counts(countall(status, names, LOGS), counts(names, numbers), status=0,
                 hint=PASS_ON_HINT)
