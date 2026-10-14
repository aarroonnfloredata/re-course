"""Checks for the inline challenges in lesson.md."""

import re

import pytest

from checks import check_run, log, name_error, text
from helpers import lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

# Requests from the examples in the challenge files.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048"
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"
LOGO = "2026-10-06T10:16:48 192.0.2.44 GET /logo.png 200 4096"
INDEX_AGAIN = "2026-10-06T10:16:48 192.0.2.44 GET /index.html 200 512"
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
UPLOAD = "2026-10-06T10:17:30 192.0.2.44 POST /upload 500 0"

# More requests.
MOVED = "2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 0"
VIDEO = "2026-10-06T10:18:41 192.0.2.44 GET /video.mp4 200 5120"
BACKUP = "2026-10-06T10:19:02 203.0.113.5 GET /backup.tar 200 1048576"
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 9"
STYLE = "2026-10-06T10:20:12 198.51.100.7 GET /style.css 200 404"  # 404 as the bytes
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_OLD = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"

NOTES = log("Look into the 404s.")


def request(second, status, size=512):
    """A request `second` seconds after 10:20, with `status` and `size` bytes."""
    time = f"2026-10-06T10:2{second // 60}:{second % 60:02d}"
    return f"{time} 192.0.2.44 GET /page.html {status} {size}"


def spaces_hint(name):
    return (f'Put $1 in double quotes wherever you use it: "$1" keeps {name!r} in one piece, '
            "its runs of spaces too.")


# c1


C1_FIELDS_HINT = ("The path is the fourth field and the status the fifth. With -d ' ', cut "
                  "splits each line at its spaces, and -f picks the fields: -f 4,5.")
C1_TAB_HINT = ("Without -d ' ', cut splits lines at tabs, and a line without a tab comes out "
               "whole. Log lines use spaces: give cut -d ' '.")
C1_ORDER_HINT = ("Print one line for each request, in the order of LOGFILE: don't sort the "
                 "lines, and keep the ones that repeat.")
C1_SWAPPED_HINT = "Print the path first, then the status: PATH STATUS."
C1_ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'


def c1_problem(run, name, log_text, expected):
    """A hint for a mistake the run shows whatever the case is about."""
    if name_error(run):
        return spaces_hint(name)
    got, want = lines(run.stdout), lines(expected)
    if not got or got == want:
        return None
    if got == lines(log_text):
        return C1_TAB_HINT
    if [" ".join(line.split(" ")[::-1]) for line in got] == want:
        return C1_SWAPPED_HINT
    if sorted(got) == sorted(want) or (set(got) <= set(want) and len(got) < len(want)):
        return C1_ORDER_HINT
    return None


def check_c1(name, files, expected, hint):
    run = run_script(C1, name, files=files)
    expected = text(*expected)
    check_run(run, expected, hint, c1_problem(run, name, files[name], expected))


@pytest.mark.objective(1)
def test_c1_prints_the_path_and_status_of_each_request():
    check_c1("access.log", {"access.log": log(INDEX, MISSING, LOGIN), "notes.txt": NOTES},
             ["/index.html 200", "/missing.html 404", "/login 401"], C1_FIELDS_HINT)
    check_c1("empty.log", {"empty.log": "", "access.log": log(INDEX)}, [], C1_ARGUMENT_HINT)
    check_c1("access.log",
             {"access.log": log(MISSING, LOGO, INDEX, FAVICON, INDEX_AGAIN, MISSING, STATS)},
             ["/missing.html 404", "/logo.png 200", "/index.html 200", "/favicon.ico 404",
              "/index.html 200", "/missing.html 404", "/api/stats 503"], C1_ORDER_HINT)
    check_c1("monday  log.log", {"monday  log.log": log(MONDAY_INDEX, MONDAY_OLD)},
             ["/index.html 200", "/old/page.html 404"], spaces_hint("monday  log.log"))
    check_c1("  tuesday   log.log", {"  tuesday   log.log": log(UPLOAD)},
             ["/upload 500"], spaces_hint("  tuesday   log.log"))


# c2


C2_FIELD_HINT = ("Bytes is the sixth field, the last one: cut it out with cut -d ' ' -f 6, "
                 "then sort the numbers.")
C2_NUMBERS_HINT = ("Without -n, sort compares the lines as text, one character at a time, so "
                   "64 comes after 512: 6 comes after 5. Add -n to sort them as numbers.")
C2_ORDER_HINT = "Biggest first: -n sorts the numbers smallest first, and -r turns that around."
C2_REPEATS_HINT = ("Print a number once for each request that has it: don't drop repeated "
                   "lines with uniq or sort -u.")
C2_ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'


def c2_problem(run, name, expected):
    """A hint for a mistake the run shows whatever the case is about."""
    if name_error(run):
        return spaces_hint(name)
    got, want = lines(run.stdout), lines(expected)
    if len(want) < 2 or got == want:
        return None
    if sorted(got) == sorted(want):
        if got == want[::-1]:
            return C2_ORDER_HINT
        if got in (sorted(want), sorted(want, reverse=True)):
            return C2_NUMBERS_HINT
    elif set(got) == set(want) and len(got) < len(want):
        return C2_REPEATS_HINT
    return None


def check_c2(name, files, expected, hint):
    run = run_script(C2, name, files=files)
    expected = text(*expected)
    check_run(run, expected, hint, c2_problem(run, name, expected))


@pytest.mark.objective(2)
def test_c2_prints_the_bytes_biggest_first():
    check_c2("access.log",
             {"access.log": log(INDEX, MISSING, LOGIN, LOGO, FAVICON, UPLOAD), "notes.txt": NOTES},
             ["4096", "512", "153", "153", "64", "0"], C2_FIELD_HINT)
    check_c2("access.log",
             {"access.log": log(LOGIN, INDEX, MOVED, VIDEO, BACKUP, ROBOTS, STYLE, INDEX_AGAIN)},
             ["1048576", "5120", "512", "512", "404", "64", "9", "0"], C2_NUMBERS_HINT)
    check_c2("access.log", {"access.log": log(MISSING, LOGO, FAVICON, ROBOTS, FAVICON)},
             ["4096", "153", "153", "153", "9"], C2_REPEATS_HINT)
    check_c2("empty.log", {"empty.log": "", "access.log": log(INDEX)}, [], C2_ARGUMENT_HINT)
    check_c2("monday  log.log", {"monday  log.log": log(MONDAY_OLD, MONDAY_INDEX)},
             ["512", "153"], spaces_hint("monday  log.log"))
    check_c2("  tuesday   log.log", {"  tuesday   log.log": log(BACKUP)}, ["1048576"],
             spaces_hint("  tuesday   log.log"))


# c3


C3_LINE = re.compile(r"^(\S+) (\S+)$")

C3_FIELD_HINT = ("The status is the fifth field: cut -d ' ' -f 5. Count the statuses with "
                 "sort | uniq -c, then print each status and its count.")
C3_SORT_FIRST_HINT = ("uniq -c counts only repeated lines that are next to each other. Sort the "
                      "statuses before uniq -c, so equal ones come together.")
C3_PADDED_HINT = ("uniq -c puts spaces before each count. Read its lines with "
                  'while read -r count status, which drops them, and print "$status $count".')
C3_SPACING_HINT = ('Print one space between the status and its count, and no other spaces: '
                   'echo "$status $count".')
C3_SWAPPED_HINT = ("Print the status first, then its count: uniq -c puts the count first, so "
                   'read -r count status and print "$status $count".')
C3_ORDER_HINT = ("The lines come in order of status, lowest first: sort the statuses, not the "
                 "counts, and without -r.")
C3_ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'


def c3_problem(run, name, expected):
    """A hint for a mistake the run shows whatever the case is about."""
    if name_error(run):
        return spaces_hint(name)
    got, want = lines(run.stdout), lines(expected)
    if not want or not got or got == want:
        return None
    if any(not C3_LINE.match(line) for line in got):
        if any(line[:1].isspace() for line in got):
            return C3_PADDED_HINT
        if all(C3_LINE.match(" ".join(line.split())) for line in got):
            return C3_SPACING_HINT
        return None
    pairs = [C3_LINE.match(line).groups() for line in got]
    if [f"{second} {first}" for first, second in pairs] == want:
        return C3_SWAPPED_HINT
    statuses = [first for first, _ in pairs]
    if len(set(statuses)) < len(statuses):
        return C3_SORT_FIRST_HINT
    if sorted(got) == sorted(want):
        return C3_ORDER_HINT
    return None


def check_c3(name, files, expected, hint):
    run = run_script(C3, name, files=files)
    expected = text(*expected)
    check_run(run, expected, hint, c3_problem(run, name, expected))


@pytest.mark.objective(3)
def test_c3_counts_the_requests_of_each_status():
    check_c3("access.log",
             {"access.log": log(INDEX, MISSING, LOGIN, ABOUT, STATS, INDEX_AGAIN, FAVICON),
              "notes.txt": NOTES},
             ["200 3", "401 1", "404 2", "503 1"], C3_FIELD_HINT)
    check_c3("access.log", {"access.log": log(UPLOAD, STYLE, MISSING, MOVED, ROBOTS, INDEX)},
             ["200 2", "301 1", "404 2", "500 1"], C3_SORT_FIRST_HINT)
    check_c3("empty.log", {"empty.log": "", "access.log": log(INDEX)}, [], C3_ARGUMENT_HINT)
    check_c3("monday  log.log", {"monday  log.log": log(MONDAY_OLD, MONDAY_INDEX)},
             ["200 1", "404 1"], spaces_hint("monday  log.log"))
    check_c3("  tuesday   log.log", {"  tuesday   log.log": log(MISSING, FAVICON, ROBOTS)},
             ["404 3"], spaces_hint("  tuesday   log.log"))
    statuses = [404, 200, 200, 301, 200, 200, 200, 404, 200, 500, 200, 200, 200, 200]
    check_c3("access.log",
             {"access.log": log(*(request(7 * i, status) for i, status in enumerate(statuses)))},
             ["200 10", "301 1", "404 2", "500 1"], C3_SORT_FIRST_HINT)
