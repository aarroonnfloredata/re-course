"""Checks for the inline challenges in lesson.md."""

import pytest

from checks import check_run, log, name_error, spaces_hint, text
from helpers import run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"
C4 = "challenges/c4.sh"

NOTES = log("Look into the 404s.")
ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'


def check_challenge(script, name, files, expected, hint):
    """Run `script` on the log file `name` and fail unless it printed just
    the `expected` lines, nothing to stderr, exited with grep's status and
    left the files as they were."""
    run = run_script(script, name, files=files)
    check_run(run, text(*expected), hint, spaces_hint(name) if name_error(run) else None)


# c1

# Requests from the example in c1.sh.
OCT04 = "2026-10-04T23:59:58 192.0.2.44 GET /index.html 200 512"
OCT05 = "2026-10-05T08:00:03 203.0.113.5 GET /about.html 200 2048"
OCT07 = "2026-10-07T17:45:12 198.51.100.7 GET /missing.html 404 153"
OCT08_REPORT = "2026-10-08T09:30:00 192.0.2.44 GET /reports/2026-10-06.html 200 1024"
OCT15 = "2026-10-15T10:15:32 203.0.113.5 GET /index.html 200 512"

# More requests.
OCT01 = "2026-10-01T09:00:00 192.0.2.44 GET /index.html 200 512"
OCT03_REPORT = "2026-10-03T11:20:00 192.0.2.44 GET /reports/2026-10-05.html 200 1020"
OCT05_EARLY = "2026-10-05T00:00:00 198.51.100.7 GET /index.html 200 512"
OCT06 = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
OCT06_LATE = "2026-10-06T23:59:59 198.51.100.7 GET /logo.png 200 4096"
OCT07_LOGIN = "2026-10-07T12:30:45 203.0.113.5 POST /login 401 64"
OCT08 = "2026-10-08T08:00:00 203.0.113.5 GET /about.html 200 2048"
OCT09 = "2026-10-09T14:10:00 192.0.2.44 GET /index.html 200 512"
OCT09_BACKUP = "2026-10-09T03:00:00 203.0.113.5 GET /backups/2026-10-07T03.tar 200 1048576"
OCT16 = "2026-10-16T10:15:32 192.0.2.44 GET /index.html 200 512"
OCT25 = "2026-10-25T08:00:03 203.0.113.5 GET /about.html 200 2048"
OCT27 = "2026-10-27T17:45:12 198.51.100.7 GET /missing.html 404 153"
SEP06 = "2026-09-06T10:15:32 203.0.113.5 GET /index.html 200 512"
NOV05 = "2026-11-05T08:00:03 192.0.2.44 GET /about.html 200 2048"
OLD_OCT06 = "2025-10-06T10:15:32 198.51.100.7 GET /index.html 200 512"

C1_EXAMPLE_HINT = ("Print the lines whose time starts with 2026-10-05, 2026-10-06 or "
                   "2026-10-07: ^ makes a pattern match only at the start of a line, and a "
                   "bracket expression such as [567] matches one character from a set.")
C1_ANCHOR_HINT = ("Only the time counts, and it is at the start of the line: begin the pattern "
                  "with ^, so a date in the path doesn't match.")
C1_DAYS_HINT = ("Only the 5th, 6th and 7th count: after 2026-10-0, a bracket expression holding "
                "just 5, 6 and 7, [567], matches one of them.")
C1_DATE_HINT = ("Write out the year, the month and the 0 of the day, ^2026-10-0, and use a set "
                "only for the last digit. A . matches any character, so it lets other "
                "months, years and days through.")
C1_NONE_HINT = "None of these requests was made on 5, 6 or 7 October 2026: print nothing."


@pytest.mark.objective(1)
def test_c1_prints_the_requests_of_5_to_7_october():
    check_challenge(C1, "access.log",
                    {"access.log": log(OCT04, OCT05, OCT07, OCT08_REPORT, OCT15),
                     "notes.txt": NOTES},
                    [OCT05, OCT07], C1_EXAMPLE_HINT)
    check_challenge(C1, "access.log",
                    {"access.log": log(OCT08_REPORT, OCT06, OCT03_REPORT, OCT09_BACKUP)},
                    [OCT06], C1_ANCHOR_HINT)
    check_challenge(C1, "access.log",
                    {"access.log": log(OCT06_LATE, OCT04, OCT07_LOGIN, OCT08, OCT01, OCT05_EARLY,
                                       OCT09)},
                    [OCT06_LATE, OCT07_LOGIN, OCT05_EARLY], C1_DAYS_HINT)
    check_challenge(C1, "access.log",
                    {"access.log": log(SEP06, OCT16, NOV05, OCT25, OCT06, OLD_OCT06, OCT27,
                                       OCT15)},
                    [OCT06], C1_DATE_HINT)
    check_challenge(C1, "access.log", {"access.log": log(OCT04, OCT08_REPORT, OCT15)}, [],
                    C1_NONE_HINT)
    check_challenge(C1, "empty.log", {"empty.log": "", "access.log": log(OCT06, OCT07)}, [],
                    ARGUMENT_HINT)
    check_challenge(C1, "monday  log.log", {"monday  log.log": log(OCT05, OCT08, OCT06_LATE)},
                    [OCT05, OCT06_LATE], spaces_hint("monday  log.log"))
    check_challenge(C1, "  tuesday   log.log", {"  tuesday   log.log": log(OCT01, OCT07)},
                    [OCT07], spaces_hint("  tuesday   log.log"))


# c2

# Requests from the example in c2.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
ABOUT = "2026-10-06T10:15:40 198.51.100.7 GET /about.html 200 1000"
REPORT = "2026-10-06T10:16:02 192.0.2.44 GET /reports/2026.html 200 999"
LOGO = "2026-10-06T10:16:15 192.0.2.44 GET /logo.png 200 40960"
MISSING = "2026-10-06T10:16:20 203.0.113.5 GET /missing.html 404 0"

# More requests.
LOGIN = "2026-10-06T10:16:48 203.0.113.5 POST /login 401 64"
ROBOTS = "2026-10-06T10:17:03 198.51.100.7 GET /robots.txt 200 100"
STYLE = "2026-10-06T10:17:30 192.0.2.44 GET /style.css 200 1001"
SCRIPT = "2026-10-06T10:17:45 192.0.2.44 GET /app.js 200 9999"
VIDEO = "2026-10-06T10:18:02 203.0.113.5 GET /video.mp4 200 10000"
FAVICON = "2026-10-06T10:18:30 198.51.100.7 GET /favicon.ico 404 9"
BACKUP = "2026-10-06T10:19:02 203.0.113.5 GET /backup.tar 200 1048576"
PHOTO = "2026-10-06T10:19:40 192.0.2.44 GET /photo.jpg 200 2048"
ARCHIVE = "2026-10-06T10:20:12 198.51.100.7 GET /archive/20261006/list.html 200 64"
REPORT_2025 = "2026-10-06T10:20:40 192.0.2.44 GET /reports/2025.html 200 153"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_LOGO = "2026-10-05T09:13:02 203.0.113.5 GET /logo.png 200 4096"

C2_EXAMPLE_HINT = ("Bytes is the last field, so it ends the line: $. 1000 or more is a number "
                   "of 4 digits or more, and {4,} repeats [0-9] 4 or more times. { } needs "
                   "grep -E.")
C2_BOUNDARY_HINT = ("Bytes have no leading zeros, so 999 has 3 digits and 1000 has 4: 1000 or "
                    "more means 4 digits or more, [0-9]{4,}.")
C2_LONG_HINT = ("{4} is exactly 4 times and {4,} is 4 or more times: 40960 and 1048576 have more "
                "than 4 digits.")
C2_OTHER_FIELDS_HINT = ("Only the bytes field counts, but the time and a path hold 4 digits in a "
                        "row too. Match a space, the digits and $, the end of the line, where "
                        "the bytes are.")
C2_NONE_HINT = "None of these requests sent 1000 bytes or more: print nothing."


@pytest.mark.objective(2)
def test_c2_prints_the_requests_of_1000_bytes_or_more():
    check_challenge(C2, "access.log",
                    {"access.log": log(INDEX, ABOUT, REPORT, LOGO, MISSING), "notes.txt": NOTES},
                    [ABOUT, LOGO], C2_EXAMPLE_HINT)
    check_challenge(C2, "access.log",
                    {"access.log": log(REPORT, STYLE, ROBOTS, SCRIPT, ABOUT, LOGIN, VIDEO)},
                    [STYLE, SCRIPT, ABOUT, VIDEO], C2_BOUNDARY_HINT)
    check_challenge(C2, "access.log",
                    {"access.log": log(BACKUP, INDEX, LOGO, FAVICON, PHOTO)},
                    [BACKUP, LOGO, PHOTO], C2_LONG_HINT)
    check_challenge(C2, "access.log",
                    {"access.log": log(ARCHIVE, REPORT_2025, PHOTO, REPORT, MISSING)},
                    [PHOTO], C2_OTHER_FIELDS_HINT)
    check_challenge(C2, "access.log", {"access.log": log(INDEX, REPORT, MISSING, FAVICON)}, [],
                    C2_NONE_HINT)
    check_challenge(C2, "empty.log", {"empty.log": "", "access.log": log(ABOUT, LOGO)}, [],
                    ARGUMENT_HINT)
    check_challenge(C2, "monday  log.log", {"monday  log.log": log(MONDAY_LOGO, MONDAY_INDEX)},
                    [MONDAY_LOGO], spaces_hint("monday  log.log"))
    check_challenge(C2, "  tuesday   log.log", {"  tuesday   log.log": log(LOGIN, BACKUP)},
                    [BACKUP], spaces_hint("  tuesday   log.log"))


# c3

# Requests from the example in c3.sh.
HOME = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
HEALTH = "2026-10-06T10:15:40 127.0.0.1 GET /health 200 2"
HEALTH_TITLE = "2026-10-06T10:16:02 127.0.0.1 GET /Health 200 2"
HEALTHZ = "2026-10-06T10:16:15 192.0.2.44 GET /healthz 404 153"
API_HEALTH = "2026-10-06T10:16:20 198.51.100.7 GET /api/health 200 17"
HEALTH_UPPER = "2026-10-06T10:16:48 127.0.0.1 GET /HEALTH 200 2"

# More requests.
HEALTH_MIXED = "2026-10-06T10:17:03 127.0.0.1 GET /hEaLtH 200 2"
HEALTH_DB = "2026-10-06T10:17:30 127.0.0.1 GET /health/db 200 17"
HEALTHCHECK = "2026-10-06T10:17:45 192.0.2.44 GET /healthcheck 404 153"
MY_HEALTH = "2026-10-06T10:18:02 198.51.100.7 GET /my-health 404 153"
POST_HEALTH = "2026-10-06T10:18:30 127.0.0.1 POST /health 200 2"
HEAD_HEALTH = "2026-10-06T10:18:55 127.0.0.1 HEAD /HEALTH 200 0"
FAILED_LOGIN = "2026-10-06T10:19:10 203.0.113.5 POST /login 401 64"
MONDAY_HEALTH = "2026-10-05T09:12:44 127.0.0.1 GET /health 200 2"
MONDAY_HOME = "2026-10-05T09:13:02 192.0.2.44 GET /index.html 200 512"

C3_EXAMPLE_HINT = ("grep -v prints the lines that don't match, and -i ignores case. Leave out "
                   "the lines whose path is /health: ' /health ', with a space on each side.")
C3_CASE_HINT = "Give grep -i, so /Health, /HEALTH and /hEaLtH are left out too."
C3_EXACT_HINT = ("Only the path /health itself is left out: put a space on each side of it, "
                 "' /health ', so a longer path that holds it doesn't match.")
C3_METHOD_HINT = ("Every request for /health is left out, whatever its method: match the path "
                  "with a space on each side, ' /health ', not the method.")
C3_NONE_HINT = ("Every request here is for /health: print nothing. grep -v exits with 1 when it "
                "prints no line.")


@pytest.mark.objective(4)
def test_c3_leaves_out_the_health_requests():
    check_challenge(C3, "access.log",
                    {"access.log": log(HOME, HEALTH, HEALTH_TITLE, HEALTHZ, API_HEALTH,
                                       HEALTH_UPPER),
                     "notes.txt": NOTES},
                    [HOME, HEALTHZ, API_HEALTH], C3_EXAMPLE_HINT)
    check_challenge(C3, "access.log",
                    {"access.log": log(HEALTH_UPPER, HOME, HEALTH_MIXED, HEALTH_TITLE,
                                       FAILED_LOGIN, HEALTH)},
                    [HOME, FAILED_LOGIN], C3_CASE_HINT)
    check_challenge(C3, "access.log",
                    {"access.log": log(HEALTHZ, HEALTH, HEALTH_DB, API_HEALTH, HEALTHCHECK,
                                       MY_HEALTH)},
                    [HEALTHZ, HEALTH_DB, API_HEALTH, HEALTHCHECK, MY_HEALTH], C3_EXACT_HINT)
    check_challenge(C3, "access.log",
                    {"access.log": log(POST_HEALTH, HOME, HEAD_HEALTH, HEALTH)},
                    [HOME], C3_METHOD_HINT)
    check_challenge(C3, "access.log",
                    {"access.log": log(HEALTH, HEALTH_UPPER, POST_HEALTH, HEALTH_MIXED)}, [],
                    C3_NONE_HINT)
    check_challenge(C3, "empty.log", {"empty.log": "", "access.log": log(HOME, HEALTHZ)}, [],
                    ARGUMENT_HINT)
    check_challenge(C3, "monday  log.log",
                    {"monday  log.log": log(MONDAY_HEALTH, MONDAY_HOME)},
                    [MONDAY_HOME], spaces_hint("monday  log.log"))
    check_challenge(C3, "  tuesday   log.log",
                    {"  tuesday   log.log": log(FAILED_LOGIN, HEALTH_TITLE, API_HEALTH)},
                    [FAILED_LOGIN, API_HEALTH], spaces_hint("  tuesday   log.log"))


# c4

# Requests from the example in c4.sh.
ADMIN = "2026-10-06T10:15:32 203.0.113.5 GET /admin 200 2048"
ADMINISTRATOR = "2026-10-06T10:15:40 198.51.100.7 GET /administrator 404 153"
LOGIN_PAGE = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
LOGIN_PHP = "2026-10-06T10:16:15 192.0.2.44 GET /login.php 404 153"
ADMIN_USERS = "2026-10-06T10:16:20 192.0.2.44 GET /admin/users 200 4096"
API_LOGIN = "2026-10-06T10:16:48 198.51.100.7 POST /api/login 200 128"
LOGIN_RESET = "2026-10-06T10:17:03 192.0.2.44 GET /login/reset 200 512"
BLOG_ADMIN = "2026-10-06T10:17:30 203.0.113.5 GET /blog/admin/tips 200 1024"

# More requests.
ADMIN_SLASH = "2026-10-06T10:17:45 192.0.2.44 GET /admin/ 200 2048"
LOGIN_SLASH = "2026-10-06T10:18:02 203.0.113.5 GET /login/ 200 512"
ADMIN_TIPS = "2026-10-06T10:18:15 198.51.100.7 GET /admin-tips 200 1024"
LOGINHELP = "2026-10-06T10:18:30 192.0.2.44 GET /loginhelp 404 153"
ADMINS = "2026-10-06T10:18:48 203.0.113.5 GET /admins 404 153"
ADMIN_EDIT = "2026-10-06T10:19:02 192.0.2.44 POST /admin/users/7/edit 200 64"
API_LOGIN_RESET = "2026-10-06T10:19:20 198.51.100.7 GET /api/login/reset 404 153"
SHOP_ADMIN = "2026-10-06T10:19:40 203.0.113.5 GET /shop/admin 404 153"
HEAD_ADMIN = "2026-10-06T10:20:05 192.0.2.44 HEAD /admin 200 0"
DELETE_LOGIN = "2026-10-06T10:20:30 203.0.113.5 DELETE /login/sessions 204 0"
FRONT_PAGE = "2026-10-06T10:20:48 198.51.100.7 GET /index.html 200 512"
MONDAY_ADMIN = "2026-10-05T09:12:44 192.0.2.44 GET /admin/logs 200 4096"
MONDAY_FRONT = "2026-10-05T09:13:02 203.0.113.5 GET /index.html 200 512"

C4_EXAMPLE_HINT = ("Match a space, a / and one of the two names, grouped with ( ) and |: "
                   "' /(admin|login)'. Right after the name, the path either ends, with the "
                   "space before the status, or goes on with a /. ( ) and | need grep -E.")
C4_END_HINT = ("A path that only starts with the same letters doesn't count: right after admin "
               "or login comes either the space that ends the path or a /, as in /admin/ and "
               "/login/.")
C4_START_HINT = ("Only paths that start with /admin or /login count: put a space before the /, "
                 "' /(admin|login)', so a name further on in the path doesn't match.")
C4_METHOD_HINT = "Any method counts: match the path, not the method."
C4_NONE_HINT = "None of these requests is for an admin or login page: print nothing."


@pytest.mark.objective(3)
def test_c4_prints_the_requests_for_admin_and_login_pages():
    check_challenge(C4, "access.log",
                    {"access.log": log(ADMIN, ADMINISTRATOR, LOGIN_PAGE, LOGIN_PHP, ADMIN_USERS,
                                       API_LOGIN, LOGIN_RESET, BLOG_ADMIN),
                     "notes.txt": NOTES},
                    [ADMIN, LOGIN_PAGE, ADMIN_USERS, LOGIN_RESET], C4_EXAMPLE_HINT)
    check_challenge(C4, "access.log",
                    {"access.log": log(ADMINISTRATOR, ADMIN_SLASH, ADMIN_TIPS, LOGIN_PHP,
                                       LOGINHELP, LOGIN_SLASH, ADMINS)},
                    [ADMIN_SLASH, LOGIN_SLASH], C4_END_HINT)
    check_challenge(C4, "access.log",
                    {"access.log": log(API_LOGIN, ADMIN_EDIT, BLOG_ADMIN, API_LOGIN_RESET,
                                       SHOP_ADMIN, LOGIN_PAGE)},
                    [ADMIN_EDIT, LOGIN_PAGE], C4_START_HINT)
    check_challenge(C4, "access.log",
                    {"access.log": log(HEAD_ADMIN, FRONT_PAGE, DELETE_LOGIN, LOGIN_PAGE)},
                    [HEAD_ADMIN, DELETE_LOGIN, LOGIN_PAGE], C4_METHOD_HINT)
    check_challenge(C4, "access.log",
                    {"access.log": log(ADMINISTRATOR, API_LOGIN, FRONT_PAGE, LOGINHELP)}, [],
                    C4_NONE_HINT)
    check_challenge(C4, "empty.log", {"empty.log": "", "access.log": log(ADMIN, LOGIN_PAGE)},
                    [], ARGUMENT_HINT)
    check_challenge(C4, "monday  log.log",
                    {"monday  log.log": log(MONDAY_FRONT, MONDAY_ADMIN)},
                    [MONDAY_ADMIN], spaces_hint("monday  log.log"))
    check_challenge(C4, "  tuesday   log.log",
                    {"  tuesday   log.log": log(LOGIN_RESET, ADMINS)},
                    [LOGIN_RESET], spaces_hint("  tuesday   log.log"))
