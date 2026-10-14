"""Checks for the inline challenges in lesson.md."""

import pytest

from checks import check_files_unchanged, log
from helpers import check, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"
C4 = "challenges/c4.sh"

INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"

TAIL_HINT = "The second line is the last line of LOGFILE: tail -n 1 prints it."
SPACES_HINT = ('Put $1 in double quotes everywhere you use it, in the echo line and in the '
               'tail command: "$1" stays one argument, with all its spaces.')
GLOB_NAME_HINT = ('Quoted, "$1" is plain text. Unquoted, a name with * ? or [ ] is a glob, and '
                  "bash replaces it with the names of other files.")


def check_last_request(name, files, last, hint):
    run = run_script(C1, name, files=files)
    check(run, stdout=f"Last request in {name}:\n{last}", hint=hint)
    check(run, stderr="")
    check_files_unchanged(run)


@pytest.mark.objective(2)
def test_c1_prints_the_last_request_of_the_named_log():
    check_last_request("access.log", {"access.log": log(INDEX, LOGIN, MISSING)}, MISSING,
                       TAIL_HINT)
    check_last_request("monday  log.log", {"monday  log.log": log(INDEX, MISSING)}, MISSING,
                       SPACES_HINT)
    check_last_request(" access.log",
                       {" access.log": log(MISSING, LOGIN), "access.log": log(LOGIN, INDEX)},
                       LOGIN, SPACES_HINT)
    check_last_request("*.log", {"*.log": log(INDEX, FAVICON), "access.log": log(MISSING)},
                       FAVICON, GLOB_NAME_HINT)
    check_last_request("[old].log", {"[old].log": log(INDEX, LOGIN), "o.log": log(MISSING)},
                       LOGIN, GLOB_NAME_HINT)


@pytest.mark.objective(3)
def test_c2_prints_the_grep_command_as_text():
    run = run_script(C2, "404")
    check(run, stdout='grep -c " 404 " "$logfile"',
          hint=r'Inside double quotes, \$ gives a plain $ and \" a plain "; inside single '
               "quotes everything stays as it is, $1 too.")
    check(run, stderr="")
    check(run_script(C2, "500"), stdout='grep -c " 500 " "$logfile"',
          hint="STATUS is the argument, $1: it is the only part that changes.")


# The logs of the example in c3.sh.
SEPT_30 = "2026-09-30T23:50:12 192.0.2.44 GET /missing.html 404 153"
OCT_5_ABOUT = "2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048"
OCT_5_OLD_PAGE = "2026-10-05T23:59:30 203.0.113.5 GET /old/page.html 404 153"
OCT_6_MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
OCT_6_FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
EXAMPLE_LOGS = {
    "access-2026-09-30.log": log(SEPT_30),
    "access-2026-10-05.log": log(OCT_5_ABOUT, OCT_5_OLD_PAGE),
    "access-2026-10-06.log": log(OCT_6_MISSING, OCT_6_FAVICON),
    "access.log": log(OCT_6_MISSING),
}


def request(day, path, status, size=153):
    return f"{day}T12:00:00 192.0.2.44 GET {path} {status} {size}"


# November's logs, among files whose names are close to them.
NOVEMBER_AMONG_OTHER_FILES = {
    "access-2026-11-01.log": log(request("2026-11-01", "/index.html", 200, 512),
                                 request("2026-11-01", "/missing.html", 404)),
    "access-2026-11-02.log": log(request("2026-11-02", "/favicon.ico", 404),
                                 request("2026-11-02", "/robots.txt", 404)),
    "access-2026-11.log": log(request("2026-11-30", "/summary.html", 404)),
    "access-2026-11-03.log.old": log(request("2026-11-03", "/old.html", 404)),
    "access-2026-10-31.log": log(request("2026-10-31", "/missing.html", 404)),
    "access-2026-12-01.log": log(request("2026-12-01", "/missing.html", 404)),
    "access.log": log(request("2026-11-02", "/missing.html", 404)),
    "notes.txt": "Look into the 404 requests of November.\n",
}

# November's logs, with 404 in other fields too.
NOVEMBER_WITH_404_ELSEWHERE = {
    "access-2026-11-01.log": log(request("2026-11-01", "/missing.html", 404),
                                 request("2026-11-01", "/about.html", 200, 404),
                                 request("2026-11-01", "/errors/404.html", 200, 1024)),
    "access-2026-11-02.log": log(request("2026-11-02", "/status/404", 200, 512),
                                 request("2026-11-02", "/logo.png", 200, 4040),
                                 request("2026-11-02", "/favicon.ico", 404)),
}

# August's logs, without a 404 request.
AUGUST_WITHOUT_404 = {
    "access-2026-08-01.log": log(request("2026-08-01", "/index.html", 200, 512)),
    "access-2026-08-02.log": log(request("2026-08-02", "/upload", 500, 0)),
    "access.log": log(OCT_6_MISSING),
}


@pytest.mark.objective(4)
def test_c3_counts_the_404_requests_of_a_month():
    run = run_script(C3, "2026-10", files=EXAMPLE_LOGS)
    check(run, stdout="2026-10: 3 requests with status 404",
          hint="Inside double quotes, * is plain text: keep MONTH in the quotes and the glob "
               "characters outside them, and send all the files through cat into one grep -c.")
    check(run, stderr="")
    check_files_unchanged(run, hint="cat ... | grep -c passes the lines on through a pipe, "
                                    "so no file is needed.")

    check(run_script(C3, "2026-09", files=EXAMPLE_LOGS),
          stdout="2026-09: 1 requests with status 404",
          hint='MONTH is the argument, $1: build the names from it, and the line always says '
               '"requests".')
    check(run_script(C3, "2026-11", files=NOVEMBER_AMONG_OTHER_FILES),
          stdout="2026-11: 3 requests with status 404",
          hint="Only the files whose names start with access-MONTH- (with the - after MONTH) "
               "and end with .log count.")
    check(run_script(C3, "2026-11", files=NOVEMBER_WITH_404_ELSEWHERE),
          stdout="2026-11: 2 requests with status 404",
          hint='A request has status 404 when its line contains " 404 ", with a space on each '
               "side, so 404 in the path or the bytes doesn't count.")

    run = run_script(C3, "2026-08", files=AUGUST_WITHOUT_404)
    check(run, stdout="2026-08: 0 requests with status 404", status=run.status,
          hint="grep -c prints 0 when no line matches.")
    check(run, hint="Exit with status 0, also when N is 0: a script ends with the status of "
                    "its last command.")


# The logs of the examples in c4.sh.
MONDAY = "monday  log.log"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
MONDAY_OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"
C4_LOGS = {MONDAY: log(MONDAY_INDEX, MONDAY_OLD_PAGE), "access.log": log(MISSING, LOGIN, FAVICON)}

FILES_QUOTED_HINT = ('"$@" gives each FILE as one argument, spaces and all. Without quotes, $@ '
                     'and $* split the names at the spaces, and "$*" joins all the names into one.')


def check_most_recent(args, files, expected, hint):
    run = run_script(C4, *args, files=files)
    check(run, stdout=log(*expected), status=run.status, hint=hint)
    check(run, stderr="", status=run.status,
          hint='If cat complains about a file named N, keep N in a variable and shift it away '
               'first: then "$@" holds only the FILEs.')
    check(run, hint="Exit with status 0: a script ends with the status of its last command.")
    check_files_unchanged(run, hint="cat ... | tail -n N passes the lines on through a pipe, "
                                    "so no file is needed.")


@pytest.mark.objective(5)
def test_c4_prints_the_last_n_lines_of_the_files_together():
    check_most_recent(["4", "access-2026-10-05.log", "access.log"],
                      {"access-2026-10-05.log": log(MONDAY_INDEX, MONDAY_OLD_PAGE),
                       "access.log": log(MISSING, LOGIN, FAVICON)},
                      [MONDAY_OLD_PAGE, MISSING, LOGIN, FAVICON],
                      hint='Keep N in a variable, then shift: after that, $1 is the first FILE '
                           'and "$@" all of them. cat sends the lines of all the FILEs, one '
                           'after another, into one tail -n N.')
    check_most_recent(["4", MONDAY, "access.log"], C4_LOGS,
                      [MONDAY_OLD_PAGE, MISSING, LOGIN, FAVICON], FILES_QUOTED_HINT)
    check_most_recent(["2", "access.log", MONDAY], C4_LOGS, [MONDAY_INDEX, MONDAY_OLD_PAGE],
                      hint="Take the FILEs in the order given: the last lines are those of the "
                           "last FILE.")
    check_most_recent(["10", MONDAY, "access.log"], C4_LOGS,
                      [MONDAY_INDEX, MONDAY_OLD_PAGE, MISSING, LOGIN, FAVICON],
                      hint="When the FILEs hold N lines or fewer, print all of them.")
    check_most_recent(["5", "access.log"],
                      {"5": log(INDEX), "access.log": log(MISSING, LOGIN, FAVICON)},
                      [MISSING, LOGIN, FAVICON],
                      hint="N is not a FILE, even when a file named 5 is in the folder: keep N in "
                           'a variable and shift it away, so that "$@" holds only the FILEs.')
    check_most_recent(["3", " access.log"],
                      {" access.log": log(MISSING, LOGIN), "access.log": log(INDEX)},
                      [MISSING, LOGIN],
                      hint='Unquoted, $@ drops the space at the start of " access.log" and '
                           'reads access.log instead. "$@" keeps each FILE as it is.')
    check_most_recent(["10", "*.log", "[old].log"],
                      {"*.log": log(INDEX, FAVICON), "[old].log": log(LOGIN),
                       "access.log": log(MISSING), "o.log": log(OCT_5_ABOUT)},
                      [INDEX, FAVICON, LOGIN],
                      hint='Quoted, "$@" passes each name as plain text. Unquoted, a name with '
                           '* ? or [ ] is a glob, and bash replaces it with the names of other '
                           'files.')
    check_most_recent(["3", "access-2026-10-07.log", "access-2026-10-08.log"],
                      {"access-2026-10-07.log": "", "access-2026-10-08.log": ""}, [],
                      hint="When every FILE is empty, print nothing, not even an empty line.")
