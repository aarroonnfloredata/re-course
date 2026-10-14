"""Checks for the inline challenges in lesson.md."""

import pytest

from checks import check_file_holds, check_files_unchanged, log
from helpers import check, lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"
C4 = "challenges/c4.sh"

# Requests from the examples in the challenge files.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"

# More requests.
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 153"
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"  # 503, not 500
FORM = "2026-10-06T10:18:12 192.0.2.44 POST /form 500 64"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
ERROR_404_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024"  # 404 in the path
ERROR_500_PAGE = "2026-10-06T10:16:50 192.0.2.44 GET /errors/500.html 200 1024"  # 500 in the path
LOGO = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 500"  # 500 as the bytes
POST_DOCS = "2026-10-06T10:18:45 203.0.113.5 GET /docs/POST.html 200 2048"  # POST in the path


def request(second, path):
    """A request with status 404."""
    return f"2026-10-06T10:20:{second:02} 192.0.2.44 GET {path} 404 153"


SPACES_HINT = ('Put $1 in double quotes wherever you use it: "$1" keeps a name with spaces in '
               "one piece.")


def name_hint(run, hint):
    """SPACES_HINT when grep got a wrong name, else `hint`."""
    return SPACES_HINT if "No such file" in run.stderr else hint


# c1


C1_COUNT_HINT = ('First run grep -c " 404 " on "$1": it prints the count itself. Then print the '
                 "line with grep's exit status, S.")
C1_STATUS_HINT = ("S is grep's status: 1 when no line matches. $? changes after every command, "
                  "echo included, so save it in a variable straight after grep.")
C1_EXIT_HINT = ("Exit with grep's status, S. By the time exit runs, $? holds the status of the "
                "echo before it, 0: use the status you saved straight after grep.")


def check_c1(name, files, count, status, hint):
    run = run_script(C1, name, files=files)
    check(run, stdout=f"{count}\ngrep exited with {status}", status=run.status,
          hint=name_hint(run, hint))
    check(run, stderr="", status=run.status)
    check(run, status=status, hint=C1_EXIT_HINT)
    check_files_unchanged(run)


@pytest.mark.objective(1)
def test_c1_reports_and_exits_with_grep_status():
    check_c1("access.log", {"access.log": log(INDEX, MISSING, FAVICON)}, 2, 0, C1_COUNT_HINT)
    check_c1("quiet.log", {"quiet.log": log(INDEX), "access.log": log(MISSING)}, 0, 1,
             C1_STATUS_HINT)
    check_c1("monday  log.log", {"monday  log.log": log(INDEX, OLD_PAGE, LOGIN)}, 1, 0,
             SPACES_HINT)
    check_c1("empty.log", {"empty.log": ""}, 0, 1, C1_STATUS_HINT)


# c2


SAVED = "500 requests saved to server-errors.log"
OLD = log("2026-09-30T23:50:12 192.0.2.44 GET /old.html 404 153")  # from an earlier run
AND_OR_HINT = ("Step 1 prints its line only when grep finds a 500 request: &&. Step 2 prints "
               "its line only when grep finds no 404 request: ||.")
ORDER_HINT = ("Do step 1, the 500 requests, before step 2, the 404 requests, and print "
              'LOGFILE exactly as given: "$1" in double quotes keeps its spaces.')
REPLACE_HINT = "> replaces what a file held; >> adds to it."
WRITE_BOTH_HINT = ("Write both files every time, also when no line matches: grep's output sent "
                   "to a file with > replaces what the file held, and leaves it empty when "
                   "nothing matches.")
C2_PATTERN_HINT = ('A request has status 500 when its line contains " 500 ", with a space on each '
                   "side: 503, or 500 in the path or the bytes, doesn't count. The same goes for "
                   '" 404 ".')
C2_STATUS_HINT = ("Exit with status 0 every time. A script without exit ends with the status of "
                  "its last command: make sure that is not a grep that found nothing.")


def check_c2(name, files, stdout, server_errors, notfound, hint):
    run = run_script(C2, name, files=files)
    check(run, stdout=stdout, status=run.status, hint=name_hint(run, hint))
    check(run, stderr="", status=run.status)
    for file, expected in [("server-errors.log", server_errors), ("notfound.log", notfound)]:
        if file not in run.files or run.files[file] == run.given.get(file):
            file_hint = WRITE_BOTH_HINT
        elif OLD in run.files[file]:
            file_hint = REPLACE_HINT
        else:
            file_hint = name_hint(run, C2_PATTERN_HINT)
        check_file_holds(run, file, expected, hint=file_hint)
    check(run, status=0, hint=C2_STATUS_HINT)
    check_files_unchanged(run, written=("server-errors.log", "notfound.log"))


@pytest.mark.objective(2)
def test_c2_saves_the_requests_and_reports_on_them():
    old = {"server-errors.log": OLD, "notfound.log": OLD, "notes.txt": "Look into the 500s.\n"}
    check_c2("access.log", {"access.log": log(INDEX, MISSING, UPLOAD), **old},
             SAVED, log(UPLOAD), log(MISSING), AND_OR_HINT)
    check_c2("quiet.log", {"quiet.log": log(INDEX), **old},
             "no 404 requests in quiet.log", "", "", AND_OR_HINT)
    check_c2("monday.log", {"monday.log": log(INDEX, OLD_PAGE, ROBOTS), **old},
             "", "", log(OLD_PAGE, ROBOTS), AND_OR_HINT)
    check_c2("monday  log.log", {"monday  log.log": log(UPLOAD, INDEX, FORM), **old},
             f"{SAVED}\nno 404 requests in monday  log.log", log(UPLOAD, FORM), "", ORDER_HINT)
    check_c2("access.log",
             {"access.log": log(STATS, ERROR_500_PAGE, LOGO, UPLOAD, ABOUT, ERROR_404_PAGE,
                                MISSING), **old},
             SAVED, log(UPLOAD), log(MISSING), C2_PATTERN_HINT)


# c3


POST_FIRST_HINT = ("Check for POST requests first, with if: a file with both GET and POST requests "
                   "has POST requests. Only the first condition that succeeds runs its branch.")
ELIF_HINT = ('When there is no POST request, check for GET requests with elif grep -q " GET " '
             '"$1".')
ELSE_HINT = ("An empty file holds no request: grep -q fails for both POST and GET, so the else "
             "branch runs.")
POST_ONLY_HINT = "Case 1 applies to any POST request, with or without GET requests."
C3_PATTERN_HINT = ('A POST request is a line that contains " POST ", with a space on each side: '
                   "POST in the path doesn't count.")
QUIET_HINT = ("Use grep -q in each condition: it prints nothing, so only its exit status "
              "counts.")
C3_STATUS_HINT = "Exit with status 0 in every case, also when LOGFILE has no requests."


def check_c3(name, files, verdict, hint):
    run = run_script(C3, name, files=files)
    logged = {line for text in run.given.values() for line in lines(text)}
    if "No such file" not in run.stderr and logged & set(lines(run.stdout)):
        hint = QUIET_HINT
    check(run, stdout=f"{name} has {verdict}", status=run.status, hint=name_hint(run, hint))
    check(run, stderr="", status=run.status)
    check(run, status=0, hint=C3_STATUS_HINT)
    check_files_unchanged(run)


@pytest.mark.objective(3)
def test_c3_reports_which_requests_the_log_holds():
    access = {"access.log": log(INDEX, UPLOAD)}
    check_c3("access.log", access, "POST requests", POST_FIRST_HINT)
    check_c3("monday.log", {"monday.log": log(INDEX, MISSING), **access},
             "only GET requests", ELIF_HINT)
    check_c3("empty.log", {"empty.log": "", **access}, "no requests", ELSE_HINT)
    check_c3("forms.log", {"forms.log": log(LOGIN, FORM)}, "POST requests", POST_ONLY_HINT)
    check_c3("monday  log.log", {"monday  log.log": log(INDEX, OLD_PAGE)},
             "only GET requests", SPACES_HINT)
    check_c3("docs.log", {"docs.log": log(INDEX, POST_DOCS, MISSING)},
             "only GET requests", C3_PATTERN_HINT)


# c4


C4_COUNT_HINT = ('Keep N, the output of grep -c " 404 " "$1", in a variable with $( ), and '
                 "compare it with LIMIT, $2.")
EQUAL_HINT = "N equal to LIMIT is OK: only more than LIMIT is too many, and -gt means more than."
TEXT_HINT = ("Compare the numbers with -gt: > compares text by sort order, and as text {n} "
             "comes {where} {limit}.")
ZERO_HINT = "grep -c prints 0 when no line matches, and 0 is not more than 0."
C4_PATTERN_HINT = ('Count the lines that contain " 404 ", with a space on each side, so 404 in '
                   "the path or the bytes doesn't count.")


def check_c4(name, limit, files, n, hint):
    run = run_script(C4, name, str(limit), files=files)
    more = n > limit
    verdict = f"more than {limit}" if more else "OK"
    check(run, stdout=f"{n} requests with status 404: {verdict}", status=run.status,
          hint=name_hint(run, hint))
    check(run, stderr="", status=run.status)
    if more:
        check(run, status=1, hint="Exit with status 1 when N is more than LIMIT.")
    else:
        check(run, status=0, hint="Exit with status 0 when N is LIMIT or less.")
    check_files_unchanged(run)


@pytest.mark.objective(4)
def test_c4_compares_the_404_count_with_the_limit():
    access = {"access.log": log(INDEX, MISSING, FAVICON)}
    check_c4("access.log", 1, access, 2, C4_COUNT_HINT)
    check_c4("access.log", 2, access, 2, EQUAL_HINT)
    check_c4("access.log", 10, access, 2,
             TEXT_HINT.format(n=2, where="after", limit=10))
    ten = {"access.log": log(*[request(second, f"/page{second}.html") for second in range(10)])}
    check_c4("access.log", 9, ten, 10, TEXT_HINT.format(n=10, where="before", limit=9))
    check_c4("quiet.log", 0, {"quiet.log": log(INDEX, LOGIN)}, 0, ZERO_HINT)
    check_c4("monday  log.log", 1,
             {"monday  log.log": log(MISSING, ABOUT, ERROR_404_PAGE, INDEX, FAVICON)}, 2,
             C4_PATTERN_HINT)
