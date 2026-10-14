"""Tests for exercise/suspicious.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh,
exercise/healthcheck.sh, exercise/summary.sh and exercise/top.sh are the
finished tools of modules 1 to 6, carried over unchanged, so they have no
tests here.
"""

import pytest

from checks import check_run, glob_hint, log, name_error, spaces_hint, text
from helpers import lines, run_script

SUSPICIOUS = "exercise/suspicious.sh"

# The requests of the examples in suspicious.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
TRAVERSAL = "2026-10-06T10:15:40 198.51.100.7 GET /../../etc/passwd 400 0"
WP_LOGIN = "2026-10-06T10:16:02 192.0.2.44 GET /wp-login.php 404 153"
PHP = "2026-10-06T10:16:15 192.0.2.44 GET /php 404 153"
FAILED_LOGIN = "2026-10-06T10:16:20 203.0.113.5 POST /login 401 64"
LOGIN = "2026-10-06T10:16:48 203.0.113.5 POST /login 200 128"
DOT_ENV = "2026-10-06T10:17:03 198.51.100.7 GET /.ENV 404 153"
PHP_BAK = "2026-10-06T10:17:30 192.0.2.44 GET /index.php.bak 404 153"

EXAMPLE = log(INDEX, TRAVERSAL, WP_LOGIN, PHP, FAILED_LOGIN, LOGIN, DOT_ENV, PHP_BAK)
EXAMPLE_ATTACKS = [TRAVERSAL, WP_LOGIN, FAILED_LOGIN, DOT_ENV]

# More requests.
ABOUT = "2026-10-06T10:18:05 192.0.2.44 GET /about.html 200 2048"
LOGO = "2026-10-06T10:18:40 198.51.100.7 GET /logo.png 200 4096"
STATIC = "2026-10-06T10:19:02 203.0.113.5 GET /static/..%2fconfig 404 153"
SHELL = "2026-10-06T10:19:20 192.0.2.44 GET /Shell.PhP 404 153"
LOGIN_AGAIN = "2026-10-06T10:19:45 203.0.113.5 POST /Login 401 64"
CONFIG_ENV = "2026-10-06T10:20:10 198.51.100.7 GET /config/.env 404 153"
DOTS = "2026-10-06T10:20:30 192.0.2.44 GET /a..b 404 153"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_ENV = "2026-10-05T09:13:02 203.0.113.5 GET /.env 404 153"
MONDAY_LOGIN = "2026-10-05T09:14:30 198.51.100.7 POST /login 401 64"

NOTES = log("Look into the 404s.")


def request(method, path, status=404, size=153):
    """The request a test is about. Tests put it between ABOUT and LOGO."""
    return f"2026-10-06T10:18:17 203.0.113.5 {method} {path} {status} {size}"


EXAMPLE_HINT = ("Join the three rules into one pattern with |, and give grep -E, for | and "
                "( ), and -i, to ignore case.")
TWO_DOTS_HINT = (r"A . matches any character; \. matches a real dot. Two dots in a row "
                 r"anywhere, \.\. or \.{2}, can only be in the path: the IP's dots are never "
                 "next to each other.")
SINGLE_DOTS_HINT = (r"Only two dots next to each other count. On its own, . matches any "
                    r"character, so '..' matches any two characters: write \.\. or \.{2} for "
                    "two real dots.")
ENDS_IN_HINT = (r"A path ends in .php or .env when the space before the status comes right "
                r"after it: \.(php|env) and a space. The ( ) keep the | inside the group.")
NOT_AT_END_HINT = (r"Only a path that ends in .php or .env counts: put the space that follows "
                   r"the path right after (php|env), and write \. for the dot, since . on its "
                   "own matches any character.")
LOGIN_HINT = ("A failed login is the method, the path and the status together: ' POST /login "
              "401 ', with a space after /login and on each side of 401.")
NOT_LOGIN_HINT = ("Only POST, the path /login itself and the status 401 together make a failed "
                  "login: ' POST /login 401 ', with a space after /login and on each side of "
                  "401, so other methods, paths and statuses don't match.")
CASE_HINT = "Give grep -i, so case doesn't matter: .php then matches .PHP, and /login /Login."
ONCE_HINT = ("Use one grep command with the three rules joined by |: grep prints each line "
             "once, however many of the alternatives it matches.")
ORDER_HINT = ("Print the requests in the order of LOGFILE: one grep command with the three "
              "rules joined by | reads the file once, from top to bottom.")
STATUS_HINT = ("Exit with grep's own status: 0 when it printed a line, 1 when it printed none. "
               "Use one grep command for the three rules and make it the script's last "
               "command, with nothing after it, such as an echo or exit 0.")
CLEAN_HINT = "None of these requests looks like an attack: print nothing."
ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'


def problem(run, name, expected):
    """A hint for a mistake the run shows whatever the test is about."""
    if name_error(run):
        return spaces_hint(name)
    got, want = lines(run.stdout), lines(expected)
    if not got or got == want:
        return None
    if len(set(got)) < len(got) and set(got) <= set(want):
        return ONCE_HINT
    if sorted(got) == sorted(want):
        return ORDER_HINT
    return None


def check_suspicious(name, files, attacks, hint):
    """Run suspicious.sh on `name` and fail unless it printed just the
    `attacks`, nothing to stderr, exited with grep's status (1 when there are
    none) and left the files as they were."""
    run = run_script(SUSPICIOUS, name, files=files)
    expected = text(*attacks)
    check_run(run, expected, hint, problem(run, name, expected), STATUS_HINT)


def check_one(line, is_attack, hint):
    """Check `line` alone, between two plain requests."""
    check_suspicious("access.log", {"access.log": log(ABOUT, line, LOGO)},
                     [line] if is_attack else [], hint)


@pytest.mark.objective(1, 2, 3, 4)
def test_the_example():
    check_suspicious("access.log", {"access.log": EXAMPLE, "notes.txt": NOTES},
                     EXAMPLE_ATTACKS, EXAMPLE_HINT)


@pytest.mark.objective(3)
def test_a_clean_log_prints_nothing():
    check_suspicious("clean.log", {"clean.log": log(INDEX), "access.log": EXAMPLE}, [],
                     CLEAN_HINT)


@pytest.mark.objective(3)
def test_an_empty_log_prints_nothing():
    check_suspicious("empty.log", {"empty.log": "", "access.log": EXAMPLE}, [], ARGUMENT_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "path",
    ["/../etc/passwd", "/static/..%2fconfig", "/a..b", "/files/..", "/..", "/a...b"],
)
def test_two_dots_in_a_row(path):
    check_one(request("GET", path), True, TWO_DOTS_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize("path", ["/index.html", "/a.b.c", "/v1.2/app.min.js", "/.well-known/x.y"])
def test_single_dots_dont_count(path):
    check_one(request("GET", path, 200, 512), False, SINGLE_DOTS_HINT)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "path",
    ["/wp-login.php", "/phpmyadmin/index.php", "/.env", "/config/.env", "/app/v1.2/.env"],
)
def test_paths_ending_in_php_or_env(path):
    check_one(request("GET", path), True, ENDS_IN_HINT)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "path",
    ["/php", "/env", "/index.php.bak", "/phpinfo", "/.environment", "/.env.local",
     "/shop.php/cart"],
)
def test_other_paths_with_php_or_env(path):
    check_one(request("GET", path), False, NOT_AT_END_HINT)


@pytest.mark.objective(1, 3)
def test_a_failed_login():
    check_one(request("POST", "/login", 401, 64), True, LOGIN_HINT)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "method, path, status, size",
    [
        ("GET", "/login", 401, 64),
        ("POST", "/login", 200, 128),
        ("POST", "/login", 403, 64),
        ("POST", "/login", 200, 401),
        ("POST", "/login/reset", 401, 64),
        ("POST", "/api/login", 401, 64),
    ],
    ids=["get", "status-200", "status-403", "401-as-the-bytes", "longer-path", "other-folder"],
)
def test_other_logins(method, path, status, size):
    check_one(request(method, path, status, size), False, NOT_LOGIN_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "method, path, status",
    [
        ("GET", "/WP-LOGIN.PHP", 404),
        ("GET", "/Shell.PhP", 404),
        ("GET", "/.Env", 404),
        ("GET", "/Config/.eNv", 404),
        ("POST", "/Login", 401),
        ("POST", "/LOGIN", 401),
    ],
)
def test_case_doesnt_matter_in_paths(method, path, status):
    check_one(request(method, path, status), True, CASE_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize("path", ["/../wp-config.php", "/static/..%2f.env", "/a..b.PHP"])
def test_a_request_matching_two_rules_is_printed_once(path):
    check_one(request("GET", path), True, ONCE_HINT)


@pytest.mark.objective(3)
def test_keeps_the_order_of_the_log():
    attacks = [WP_LOGIN, TRAVERSAL, FAILED_LOGIN, CONFIG_ENV, STATIC, LOGIN_AGAIN, SHELL, DOTS]
    check_suspicious("access.log",
                     {"access.log": log(WP_LOGIN, INDEX, TRAVERSAL, FAILED_LOGIN, LOGIN,
                                        CONFIG_ENV, STATIC, PHP_BAK, LOGIN_AGAIN, ABOUT, SHELL,
                                        DOTS)},
                     attacks, ORDER_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "name, files, attacks, hint",
    [
        ("monday.log", {"monday.log": log(MONDAY_INDEX, MONDAY_LOGIN), "access.log": EXAMPLE},
         [MONDAY_LOGIN], ARGUMENT_HINT),
        ("logs/monday.log",
         {"logs/monday.log": log(MONDAY_ENV, MONDAY_INDEX), "access.log": EXAMPLE},
         [MONDAY_ENV], ARGUMENT_HINT),
        ("monday  log.log", {"monday  log.log": log(MONDAY_ENV, MONDAY_INDEX, MONDAY_LOGIN)},
         [MONDAY_ENV, MONDAY_LOGIN], spaces_hint("monday  log.log")),
        ("  tuesday   log.log", {"  tuesday   log.log": log(INDEX, TRAVERSAL)},
         [TRAVERSAL], spaces_hint("  tuesday   log.log")),
        ("*.log", {"*.log": log(MONDAY_INDEX, MONDAY_ENV), "access.log": EXAMPLE},
         [MONDAY_ENV], glob_hint("*.log", "access.log")),
        ("day?.log", {"day?.log": log(WP_LOGIN, ABOUT), "day1.log": log(DOT_ENV)},
         [WP_LOGIN], glob_hint("day?.log", "day1.log")),
        ("[old].log", {"[old].log": log(INDEX, STATIC), "o.log": log(SHELL)},
         [STATIC], glob_hint("[old].log", "o.log")),
    ],
    ids=["not-access-log", "in-a-subfolder", "two-spaces-in-a-row",
         "spaces-at-the-start-and-in-a-row", "star-as-a-name", "question-mark-in-a-name",
         "brackets-in-a-name"],
)
def test_reads_the_file_given(name, files, attacks, hint):
    check_suspicious(name, files, attacks, hint)
