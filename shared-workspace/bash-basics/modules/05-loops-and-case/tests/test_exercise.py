"""Tests for exercise/summary.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh and
exercise/healthcheck.sh are the finished tools of modules 1 to 4, carried
over unchanged, so they have no tests here.
"""

import re

import pytest

from checks import check_files_unchanged, check_in_folder, log
from helpers import lines, run_script

SUMMARY = "exercise/summary.sh"

# The requests of the example in summary.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024"  # 503 in the path
MOVED = "2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 0"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"

# More requests.
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"
VIDEO = "2026-10-06T10:18:41 192.0.2.44 GET /video.mp4 200 5120"
BACKUP = "2026-10-06T10:19:02 203.0.113.5 GET /backup.tar 200 1048576"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
STATUS_PAGE = "2026-10-06T10:18:05 203.0.113.5 GET /status/404 200 512"  # 404 in the path
GONE = "2026-10-06T10:18:52 192.0.2.44 GET /gone.html 404 200"  # 200 as the bytes
# Paths with backslashes, also at their end.
ATTACK = r"2026-10-06T10:18:02 192.0.2.44 GET /scripts/..\..\winnt/cmd.exe 404 153"
TRAVERSAL = r"2026-10-06T10:18:09 192.0.2.44 GET /scripts/..\ 404 153"
SHARE = r"2026-10-06T10:18:15 203.0.113.5 GET /share\ 200 2048"

NOTES = log("Look into the 404s.")
ACCESS = log(INDEX, MISSING, STATS, ERROR_PAGE, MOVED)  # 5 requests, 2 errors, 1689 bytes
MONDAY = log(MONDAY_INDEX, OLD_PAGE)  # 2 requests, 1 errors, 665 bytes
EXAMPLE = {"logs/access.log": ACCESS, "logs/monday log.log": MONDAY, "logs/empty.log": "",
           "logs/notes.txt": NOTES, "old logs/notes.txt": NOTES}

EXAMPLE_HINT = ("For each log file, R counts its lines, E the requests with a status from 400 "
                "to 599, and B adds up the sixth field, the bytes.")
NO_MATCH_HINT = ('When DIR holds no .log file, the glob "$1"/*.log stays as it is and the loop '
                 "runs once, with the pattern itself in the variable. Skip it with "
                 "[[ -e $file ]] || continue.")
OTHER_FILES_HINT = ('Loop over "$1"/*.log: it matches the names directly in DIR that end in '
                    ".log, and nothing in DIR's subfolders.")
RESET_HINT = ("Set R, E and B back to 0 at the start of each file, inside the for loop: each "
              "line counts its own file only.")
ZERO_HINT = ("Set each counter to 0 before reading a file. With an empty file the body of the "
             "while loop never runs, and a variable that was never set prints as nothing.")
PIPE_HINT = ('Put < "$file" after done instead of piping into the while loop: a loop at the end '
             "of a pipe runs in a subshell, and its counts are lost when it ends.")
ARITH_HINT = ("Count and add with arithmetic, (( errors++ )) and (( total += bytes )): "
              "total=$total+$bytes only joins text.")
ERRORS_HINT = ("A request failed when its status is from 400 to 599 (4xx and 5xx); 1xx, 2xx "
               "and 3xx are not errors. Sort the status into its class with case.")
FIELDS_HINT = ("Split each line into its six fields with read -r: the status is the fifth "
               "field and the bytes the sixth. A number in the path, or as the bytes, is not a "
               "status.")
RAW_HINT = ("Read with read -r. Without -r, read drops backslashes, and a backslash at the end "
            "of the path joins the path to the status, so the fields after it shift.")
SPACES_HINT = ('Put $1 and $file in double quotes wherever you use them, and keep the glob '
               'outside the quotes: "$1"/*.log. Quoted, a name with spaces stays in one piece, '
               "its runs of spaces too.")
DIR_GLOB_HINT = ('Keep $1 in double quotes, as in "$1"/*.log: quoted, the * ? [ ] in DIR\'s '
                 "name are plain text. Unquoted, they make a glob that matches other folders.")
FILE_GLOB_HINT = ("A file name with * ? or [ ] is a plain name: put \"$file\" in double quotes "
                  "wherever you use it.")
FILE_NAME_HINT = ('Print each file as the glob gives it: DIR exactly as given, a "/" and the '
                  'file\'s name, such as logs/access.log, or ./access.log when DIR is ".".')
NAME_HINTS = (SPACES_HINT, DIR_GLOB_HINT, FILE_GLOB_HINT, FILE_NAME_HINT)
STATUS_HINT = ("Exit with status 0. A script ends with the status of its last command, and a "
               "[[ ]] or (( )) that comes out false has status 1: [[ -e $file ]] && ... does "
               "when the glob matched nothing, [[ -e $file ]] || continue doesn't.")

# What bash prints to stderr when a name with spaces or glob characters is
# split, or replaced with other names.
NAME_ERRORS = ["No such file", "ambiguous redirect", "Is a directory", "too many arguments",
               "binary operator expected", "unary operator expected"]

SUMMARY_LINE = re.compile(r"^(.*): (\S*) requests, (\S*) errors, (\S*) bytes$")


def summary(name, requests, errors, total):
    return f"{name}: {requests} requests, {errors} errors, {total} bytes"


def parse(text):
    """The (FILE, (R, E, B)) of each line, or None if a line has another form."""
    found = [SUMMARY_LINE.match(line) for line in lines(text)]
    if not all(found):
        return None
    return [(match.group(1), match.group(2, 3, 4)) for match in found]


def running_totals(rows):
    """What the lines would say if the counters were never set back to 0."""
    totals, result = (0, 0, 0), []
    for name, numbers in rows:
        totals = tuple(total + int(number) for total, number in zip(totals, numbers))
        result.append((name, tuple(str(total) for total in totals)))
    return result


def problem(run, directory, expected):
    """A hint for a mistake the run shows whatever the test is about."""
    if not any("*" in name for name in run.given) and "*.log" in run.stdout + run.stderr:
        return NO_MATCH_HINT
    if any(error in run.stderr for error in NAME_ERRORS):
        return SPACES_HINT
    if "+" in run.stdout:
        return ARITH_HINT
    want, got = parse(expected), parse(run.stdout)
    if got and want is not None and len(want) != len(got):
        # Lines for files outside DIR: DIR was split, or used as a glob.
        if any(not name.startswith(f"{directory}/") for name, _ in got):
            return SPACES_HINT
    if not want or not got or len(want) != len(got) or want == got:
        return None
    if [numbers for _, numbers in want] == [numbers for _, numbers in got]:
        return FILE_NAME_HINT
    if [name for name, _ in want] != [name for name, _ in got]:
        return None
    if any("" in numbers for _, numbers in got):
        return ZERO_HINT
    if got == running_totals(want):
        return RESET_HINT
    if all(numbers == ("0", "0", "0") for _, numbers in got):
        return PIPE_HINT
    return None


def check_summary(directory, files, expected, hint):
    """Run summary.sh on `directory` and fail unless it printed just the
    `expected` lines, nothing to stderr, exited with 0 and left the files as
    they were."""
    run = run_script(SUMMARY, directory, files=files)
    text = "".join(f"{line}\n" for line in expected)
    found = problem(run, directory, text)
    if found in NAME_HINTS and hint in NAME_HINTS:
        found = hint
    check_in_folder(run, stdout=text, status=run.status, hint=found or hint)
    check_in_folder(run, stderr="", status=run.status, hint=found)
    check_in_folder(run, status=0, hint=STATUS_HINT)
    check_files_unchanged(run)


@pytest.mark.objective(1, 2, 3, 4)
def test_sums_up_each_log_file():
    check_summary("logs", EXAMPLE, [summary("logs/access.log", 5, 2, 1689),
                                    summary("logs/empty.log", 0, 0, 0),
                                    summary("logs/monday log.log", 2, 1, 665)], EXAMPLE_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "directory, files",
    [
        ("old logs", EXAMPLE),
        (".", {}),
        ("logs", {"logs/archive/access.log": ACCESS, "logs/notes.txt": NOTES}),
    ],
    ids=["only-notes", "an-empty-folder", "logs-only-in-a-subfolder"],
)
def test_prints_nothing_without_log_files(directory, files):
    check_summary(directory, files, [], NO_MATCH_HINT)


@pytest.mark.objective(1)
def test_leaves_out_other_files():
    files = {"logs/access.log": ACCESS, "logs/access.log.old": MONDAY, "logs/changelog": MONDAY,
             "logs/notes.txt": NOTES, "logs/archive/monday.log": MONDAY,
             "logs/archive/old.log": ACCESS}
    check_summary("logs", files, [summary("logs/access.log", 5, 2, 1689)], OTHER_FILES_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "directory, files, expected",
    [
        (".", {"access.log": ACCESS, "monday.log": MONDAY, "notes.txt": NOTES},
         [summary("./access.log", 5, 2, 1689), summary("./monday.log", 2, 1, 665)]),
        ("logs/october", {"logs/october/access.log": ACCESS, "logs/september.log": MONDAY},
         [summary("logs/october/access.log", 5, 2, 1689)]),
    ],
    ids=["the-current-folder", "a-subfolder"],
)
def test_names_each_file_as_the_glob_gives_it(directory, files, expected):
    check_summary(directory, files, expected, FILE_NAME_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "directory, files, expected, hint",
    [
        ("old  logs",
         {"old  logs/monday  log.log": MONDAY, "logs/access.log": ACCESS},
         [summary("old  logs/monday  log.log", 2, 1, 665)], SPACES_HINT),
        ("logs", {"logs/  tuesday   log.log": log(LOGIN, UPLOAD, INDEX), "logs/tuesday": NOTES},
         [summary("logs/  tuesday   log.log", 3, 2, 576)], SPACES_HINT),
        ("logs*", {"logs*/access.log": ACCESS, "logs2/monday.log": MONDAY,
                   "logs/old.log": MONDAY},
         [summary("logs*/access.log", 5, 2, 1689)], DIR_GLOB_HINT),
        ("logs [old]", {"logs [old]/access.log": ACCESS, "logs/monday.log": MONDAY,
                        "o/old.log": MONDAY},
         [summary("logs [old]/access.log", 5, 2, 1689)], DIR_GLOB_HINT),
        ("logs", {"logs/[old].log": MONDAY, "logs/notes.txt": NOTES},
         [summary("logs/[old].log", 2, 1, 665)], FILE_GLOB_HINT),
        ("logs", {"logs/access.log": ACCESS, "logs/day?.log": log(UPLOAD)},
         [summary("logs/access.log", 5, 2, 1689), summary("logs/day?.log", 1, 1, 0)],
         FILE_GLOB_HINT),
        ("logs", {"logs/*.log": MONDAY, "logs/notes.txt": NOTES},
         [summary("logs/*.log", 2, 1, 665)], FILE_GLOB_HINT),
    ],
    ids=["two-spaces-in-a-row", "spaces-at-the-start-and-in-a-row", "star-in-dir",
         "space-and-brackets-in-dir", "brackets-in-a-file-name", "question-mark-in-a-file-name",
         "star-as-a-file-name"],
)
def test_names_with_spaces_and_glob_characters(directory, files, expected, hint):
    check_summary(directory, files, expected, hint)


@pytest.mark.objective(3)
def test_counts_each_file_on_its_own():
    files = {"logs/april.log": log(INDEX, LOGIN, VIDEO), "logs/june.log": log(UPLOAD),
             "logs/may.log": log(MISSING, BACKUP)}
    check_summary("logs", files, [summary("logs/april.log", 3, 1, 5696),
                                  summary("logs/june.log", 1, 1, 0),
                                  summary("logs/may.log", 2, 1, 1048729)], RESET_HINT)


@pytest.mark.objective(2, 3)
def test_an_empty_log_file():
    check_summary("logs", {"logs/empty.log": "", "logs/notes.txt": NOTES},
                  [summary("logs/empty.log", 0, 0, 0)], ZERO_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "status, errors",
    [(status, 0) for status in [100, 101, 200, 204, 206, 301, 304, 399]]
    + [(status, 1) for status in [400, 401, 404, 418, 499, 500, 503, 599]],
)
def test_errors_are_the_4xx_and_5xx_statuses(status, errors):
    request = f"2026-10-06T10:20:00 192.0.2.44 GET /api/item {status} 64"
    check_summary("logs", {"logs/access.log": log(request)},
                  [summary("logs/access.log", 1, errors, 64)], ERRORS_HINT)


@pytest.mark.objective(2, 4)
def test_reads_the_status_and_bytes_fields():
    check_summary("logs", {"logs/access.log": log(ABOUT, STATUS_PAGE, GONE, ERROR_PAGE)},
                  [summary("logs/access.log", 4, 1, 2140)], FIELDS_HINT)


@pytest.mark.objective(2)
def test_keeps_backslashes_in_paths():
    check_summary("logs", {"logs/access.log": log(ATTACK, TRAVERSAL, SHARE)},
                  [summary("logs/access.log", 3, 2, 2354)], RAW_HINT)
