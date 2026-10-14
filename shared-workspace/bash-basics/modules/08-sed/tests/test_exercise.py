"""Tests for exercise/anonymize.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh,
exercise/healthcheck.sh, exercise/summary.sh, exercise/top.sh and
exercise/suspicious.sh are the finished tools of modules 1 to 7, carried
over unchanged, so they have no tests here.
"""

import pytest

from checks import (check_files_unchanged, check_in_folder, check_written, glob_hint, log,
                    name_error, shown, spaces_hint, text)
from helpers import lines, run_script

ANONYMIZE = "exercise/anonymize.sh"

# The requests of the example in anonymize.sh, and what they become.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.254 GET /missing.html 404 153"
GEO = "2026-10-06T10:16:02 5.5.5.5 GET /geo/192.0.2.44 200 1024"
LOGIN = "2026-10-06T10:16:20 192.0.2.0 POST /login 401 64"

INDEX_HIDDEN = "2026-10-06T10:15:32 203.0.113.0 GET /index.html 200 512"
MISSING_HIDDEN = "2026-10-06T10:15:40 198.51.100.0 GET /missing.html 404 153"
GEO_HIDDEN = "2026-10-06T10:16:02 5.5.5.0 GET /geo/192.0.2.44 200 1024"

EXAMPLE = log(INDEX, MISSING, GEO, LOGIN)
EXAMPLE_HIDDEN = [INDEX_HIDDEN, MISSING_HIDDEN, GEO_HIDDEN, LOGIN]

# Plain requests that tests put around the one they are about.
ABOUT = "2026-10-06T10:17:03 198.51.100.7 GET /about.html 200 2048"
ABOUT_HIDDEN = "2026-10-06T10:17:03 198.51.100.0 GET /about.html 200 2048"
LOGO = "2026-10-06T10:17:40 192.0.2.44 GET /logo.png 200 4096"
LOGO_HIDDEN = "2026-10-06T10:17:40 192.0.2.0 GET /logo.png 200 4096"

# Requests of other days, for other log files.
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_INDEX_HIDDEN = "2026-10-05T09:12:44 192.0.2.0 GET /index.html 200 512"
MONDAY_LOGIN = "2026-10-05T09:14:30 203.0.113.113 POST /login 401 64"
MONDAY_LOGIN_HIDDEN = "2026-10-05T09:14:30 203.0.113.0 POST /login 401 64"
SUNDAY_ADMIN = "2026-10-04T22:01:09 10.0.0.17 GET /admin 404 153"
SUNDAY_ADMIN_HIDDEN = "2026-10-04T22:01:09 10.0.0.0 GET /admin 404 153"

NOTES = log("Look into the 404s.")


def request(ip, method="GET", path="/index.html", status=200, size=512):
    """A request from `ip`, the one a test is about."""
    return f"2026-10-06T10:17:20 {ip} {method} {path} {status} {size}"


EXAMPLE_HINT = ("Use one sed -E command: match the time and the first three numbers of the IP in "
                "a group, then the last dot and number. Replace them with \\1 and .0, and write "
                'the result with > "$1.anon".')
LAST_NUMBER_HINT = ("Replace the whole last number of the IP, however many digits it has: "
                    "[0-9]+ after the IP's last dot.")
FIRST_THREE_HINT = ("Find the last number by its place, after the IP's third dot, not by its "
                    "digits: put the time and the first three numbers in a group, and write \\1 "
                    "back before .0.")
ZERO_HINT = ("Write every line of LOGFILE, also one whose IP already ends in 0: it stays as it "
             "is. Leave out -n and p.")
OTHER_FIELDS_HINT = ("Only the client IP, the second field, changes. Tie the pattern to it: "
                     "start with ^ and the time, [^ ]+, then the IP. And leave out g, which "
                     "changes every match on a line.")
EVERY_LINE_HINT = ("sed carries out s on every line of its input: write each line of LOGFILE, "
                   "changed, in the same order.")
EMPTY_HINT = ('Write sed\'s result with > "$1.anon" also when LOGFILE is empty: > creates the '
              "file.")
REPLACE_HINT = "> replaces what a file held; >> adds to it."
ARGUMENT_HINT = ('Read the file the first argument names, "$1", whatever its name, and write '
                 'to "$1.anon".')
SUBFOLDER_HINT = ('Write to "$1.anon": the path LOGFILE with .anon added, so the new file lands '
                  "in the same folder as LOGFILE.")
IN_PLACE_HINT = ("Never write to the file sed reads: > empties it before sed starts, so sed "
                 'reads nothing. Write to "$1.anon" instead.')
PRINTED_HINT = ('Write sed\'s result to the new file with > "$1.anon" instead of printing it.')
LEFT_BEHIND_HINT = ('Write sed\'s result straight to "$1.anon" with >: no other file is '
                    "needed.")


def name_hint(anon):
    return (f'Write to "$1.anon": LOGFILE with .anon added at the end, here {shown(anon)}, in '
            "the same folder as LOGFILE.")


def mistake(run, name, anon):
    """A hint for a mistake the run shows whatever the test is about."""
    if name_error(run):
        return spaces_hint(name)
    if run.files.get(name) != run.given[name]:
        return IN_PLACE_HINT
    if lines(run.stdout) and anon not in run.files:
        return PRINTED_HINT
    created = [file for file in run.files if file not in run.given and file != anon]
    if created:
        return LEFT_BEHIND_HINT if anon in run.files else name_hint(anon)
    return None


def written_mistake(run, anon, expected):
    """A hint for a mistake the lines written to `anon` show."""
    if anon not in run.files:
        return None
    got = lines(run.files[anon])
    if len(got) < len(expected) and all(line in expected for line in got):
        return ZERO_HINT
    if len(got) == len(expected):
        for got_line, expected_line in zip(got, expected):
            got_fields, expected_fields = got_line.split(" "), expected_line.split(" ")
            if (len(got_fields) == len(expected_fields) and got_fields[1] == expected_fields[1]
                    and got_fields != expected_fields):
                return OTHER_FIELDS_HINT
    return None


def check_anonymize(name, files, expected, hint=None):
    """Run anonymize.sh on `name` in a folder holding `files`, and fail unless
    it printed nothing, exited with 0, left every file but NAME.anon as it was
    and wrote the `expected` lines to NAME.anon."""
    run = run_script(ANONYMIZE, name, files=files)
    anon = f"{name}.anon"
    problem = mistake(run, name, anon)
    check_in_folder(run, stdout="", stderr="", status=0, hint=problem)
    check_files_unchanged(run, written=(anon,), hint=problem)
    check_written(run, anon, text(*expected),
                  hint=problem or written_mistake(run, anon, expected) or hint)


def check_one(line, hidden, hint):
    """Check `line` between two plain requests: it should become `hidden`."""
    check_anonymize("access.log", {"access.log": log(ABOUT, line, LOGO)},
                    [ABOUT_HIDDEN, hidden, LOGO_HIDDEN], hint)


@pytest.mark.objective(1, 2, 4)
def test_the_example():
    check_anonymize("access.log", {"access.log": EXAMPLE, "notes.txt": NOTES}, EXAMPLE_HIDDEN,
                    EXAMPLE_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "ip, hidden",
    [
        ("203.0.113.5", "203.0.113.0"),
        ("198.51.100.254", "198.51.100.0"),
        ("192.0.2.44", "192.0.2.0"),
        ("10.0.0.1", "10.0.0.0"),
        ("172.16.254.99", "172.16.254.0"),
        ("255.255.255.255", "255.255.255.0"),
        ("0.0.0.7", "0.0.0.0"),
    ],
)
def test_hides_the_whole_last_number(ip, hidden):
    check_one(request(ip), request(hidden), LAST_NUMBER_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "ip, hidden",
    [
        ("5.5.5.5", "5.5.5.0"),
        ("203.0.113.113", "203.0.113.0"),
        ("1.1.1.1", "1.1.1.0"),
        ("10.10.10.10", "10.10.10.0"),
        ("44.4.44.44", "44.4.44.0"),
        ("100.100.100.100", "100.100.100.0"),
        ("7.17.7.7", "7.17.7.0"),
    ],
)
def test_keeps_the_first_three_numbers(ip, hidden):
    check_one(request(ip), request(hidden), FIRST_THREE_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize("ip", ["192.0.2.0", "10.0.0.0", "203.0.113.0", "0.0.0.0"])
def test_an_ip_ending_in_0_stays(ip):
    check_one(request(ip), request(ip), ZERO_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "ip, hidden, method, path, status, size",
    [
        ("203.0.113.5", "203.0.113.0", "GET", "/geo/192.0.2.44", 200, 1024),
        ("203.0.113.5", "203.0.113.0", "GET", "/geo/192.0.2.44/map", 200, 2048),
        ("192.0.2.0", "192.0.2.0", "GET", "/geo/10.0.0.7", 200, 512),
        ("10.0.0.0", "10.0.0.0", "GET", "/v2.1", 200, 64),
        ("198.51.100.7", "198.51.100.0", "GET", "/v1.2.3.4", 200, 64),
        ("198.51.100.7", "198.51.100.0", "GET", "/files/2026.10.06.7", 200, 64),
        ("198.51.100.20", "198.51.100.0", "GET", "/index.html", 200, 512),
        ("203.0.113.5", "203.0.113.0", "HEAD", "/index.html", 200, 0),
        ("192.0.2.44", "192.0.2.0", "DELETE", "/api/items/7", 204, 0),
        ("198.51.100.7", "198.51.100.0", "PUT", "/files/report.txt", 201, 2048),
    ],
    ids=["ip-in-the-path", "ip-inside-the-path", "ip-in-the-path-after-a-0",
         "dotted-version-after-a-0", "dotted-version-in-the-path", "dotted-date-in-the-path",
         "time-ending-in-the-same-number", "head", "delete", "put"],
)
def test_other_fields_stay(ip, hidden, method, path, status, size):
    check_one(request(ip, method, path, status, size), request(hidden, method, path, status, size),
              OTHER_FIELDS_HINT)


@pytest.mark.objective(1)
def test_changes_every_line_in_order():
    requests = [LOGO, MONDAY_LOGIN, INDEX, SUNDAY_ADMIN, LOGIN, MISSING, ABOUT, MONDAY_INDEX, GEO]
    hidden = [LOGO_HIDDEN, MONDAY_LOGIN_HIDDEN, INDEX_HIDDEN, SUNDAY_ADMIN_HIDDEN, LOGIN,
              MISSING_HIDDEN, ABOUT_HIDDEN, MONDAY_INDEX_HIDDEN, GEO_HIDDEN]
    check_anonymize("access.log", {"access.log": log(*requests)}, hidden, EVERY_LINE_HINT)


@pytest.mark.objective(4)
def test_an_empty_log_gives_an_empty_anon_file():
    check_anonymize("empty.log", {"empty.log": "", "access.log": EXAMPLE}, [], EMPTY_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "files, expected",
    [
        ({"access.log": log(INDEX, MISSING), "access.log.anon": log(MONDAY_INDEX_HIDDEN, LOGIN)},
         [INDEX_HIDDEN, MISSING_HIDDEN]),
        ({"access.log": log(GEO, ABOUT), "access.log.anon": log(GEO_HIDDEN, ABOUT_HIDDEN)},
         [GEO_HIDDEN, ABOUT_HIDDEN]),
        ({"access.log": "", "access.log.anon": log(SUNDAY_ADMIN_HIDDEN)}, []),
    ],
    ids=["older-lines", "same-lines", "empty-log"],
)
def test_replaces_what_the_anon_file_held(files, expected):
    check_anonymize("access.log", files, expected, REPLACE_HINT)


@pytest.mark.objective(4)
def test_leaves_every_other_file_as_it_was():
    files = {"access.log": log(INDEX, LOGIN), "monday.log": log(MONDAY_INDEX),
             "monday.log.anon": log(MONDAY_LOGIN_HIDDEN), "notes.txt": NOTES}
    check_anonymize("access.log", files, [INDEX_HIDDEN, LOGIN], ARGUMENT_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "name, files, expected, hint",
    [
        ("monday.log", {"monday.log": log(MONDAY_INDEX, MONDAY_LOGIN), "access.log": EXAMPLE},
         [MONDAY_INDEX_HIDDEN, MONDAY_LOGIN_HIDDEN], ARGUMENT_HINT),
        ("logs/monday.log", {"logs/monday.log": log(MONDAY_LOGIN, MONDAY_INDEX),
                             "access.log": EXAMPLE},
         [MONDAY_LOGIN_HIDDEN, MONDAY_INDEX_HIDDEN], SUBFOLDER_HINT),
        ("monday log.log", {"monday log.log": log(MONDAY_INDEX, SUNDAY_ADMIN)},
         [MONDAY_INDEX_HIDDEN, SUNDAY_ADMIN_HIDDEN], spaces_hint("monday log.log")),
        ("monday  log.log", {"monday  log.log": log(SUNDAY_ADMIN, MONDAY_LOGIN)},
         [SUNDAY_ADMIN_HIDDEN, MONDAY_LOGIN_HIDDEN], spaces_hint("monday  log.log")),
        ("  tuesday   log.log", {"  tuesday   log.log": log(MISSING, LOGIN)},
         [MISSING_HIDDEN, LOGIN], spaces_hint("  tuesday   log.log")),
        ("logs/monday log.log", {"logs/monday log.log": EXAMPLE}, EXAMPLE_HIDDEN,
         spaces_hint("logs/monday log.log")),
        ("*.log", {"*.log": log(MONDAY_INDEX, MONDAY_LOGIN), "access.log": EXAMPLE},
         [MONDAY_INDEX_HIDDEN, MONDAY_LOGIN_HIDDEN], glob_hint("*.log", "access.log")),
        ("day?.log", {"day?.log": log(GEO, ABOUT), "day1.log": log(SUNDAY_ADMIN)},
         [GEO_HIDDEN, ABOUT_HIDDEN], glob_hint("day?.log", "day1.log")),
        ("[old].log", {"[old].log": log(LOGO, INDEX), "o.log": log(MONDAY_LOGIN)},
         [LOGO_HIDDEN, INDEX_HIDDEN], glob_hint("[old].log", "o.log")),
    ],
    ids=["not-access-log", "in-a-subfolder", "a-space", "two-spaces-in-a-row",
         "spaces-at-the-start-and-in-a-row", "a-space-in-a-subfolder", "star-as-a-name",
         "question-mark-in-a-name", "brackets-in-a-name"],
)
def test_reads_and_writes_the_file_given(name, files, expected, hint):
    check_anonymize(name, files, expected, hint)
