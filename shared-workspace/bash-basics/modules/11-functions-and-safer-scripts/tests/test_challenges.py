"""Checks for the inline challenges in lesson.md."""

import pytest

from checks import (IPS, check_keeps_variables, check_run, given_files, in_shell, log, log_of,
                    split_name, text)
from helpers import call, fail, lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

# Requests from the examples in the challenge files.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
ABOUT = "2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048"
ABOUT_404 = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
ERRORS_503 = "2026-10-06T10:15:40 198.51.100.7 GET /errors/503.html 200 404"  # 503 in the path
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"

# More requests.
ERRORS_404 = "2026-10-06T10:16:48 203.0.113.5 GET /errors/404.html 200 1024"  # 404 in the path
CODES_404 = "2026-10-06T10:17:30 192.0.2.44 GET /codes/404 200 64"  # the path ends in 404
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 153"
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"
ORDER_451 = "2026-10-06T10:15:50 192.0.2.44 GET /orders/451 200 64"  # the path ends in 451
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"


# c1


C1_ACCESS = log(INDEX, MISSING, ABOUT_404, FAVICON)
C1_MONDAY = log(MONDAY_INDEX)

C1_HINT = ('Go through the arguments with for logfile in "$@", count the 404 requests of each '
           'with grep -c " 404 " "$logfile", and print "$logfile: $count".')
C1_NONE_HINT = ('With no LOGFILE, a loop over "$@" runs no time: print nothing, and don\'t treat '
                "it as an error.")
C1_TWICE_HINT = 'Print one line for every argument, in order: a name given twice gets two lines.'
C1_PATTERN_HINT = ('Count the lines that contain " 404 ", with a space on each side: 404 in the '
                   "path, or as the bytes at the end of the line, has no space on one side.")
C1_NAMES_HINT = ('Put "$@" and $logfile in double quotes wherever you use them. Quoted, a name '
                 "keeps its runs of spaces, and its * ? [ ] are plain text. Unquoted, a name is "
                 "split at its spaces, and * ? [ ] make a glob that can match other files, such "
                 "as a.log.")
C1_STATUS_HINT = ("Return status 0. A function without return gives back the status of its "
                  "last command: grep -c returns 1 when it counts 0, so don't end with it.")


def check_c1(args, files, expected, hint):
    run = call(C1, "report_404", *args, files=files)
    problem = C1_NAMES_HINT if split_name(run, *args) else None
    check_run(run, expected, hint=hint, status_hint=C1_STATUS_HINT, problem=problem)


@pytest.mark.objective(1)
def test_c1_reports_the_404s_of_each_file():
    files = {"access.log": C1_ACCESS, "monday log.log": C1_MONDAY}
    check_c1(["access.log", "monday log.log"], files,
             text("access.log: 2", "monday log.log: 0"), C1_HINT)
    check_c1([], files, "", C1_NONE_HINT)
    check_c1(["access.log", "access.log"], files, text("access.log: 2", "access.log: 2"),
             C1_TWICE_HINT)

    decoys = {"decoys.log": log(ERRORS_404, MISSING, ABOUT_404, CODES_404, FAVICON, ROBOTS)}
    check_c1(["decoys.log"], decoys, "decoys.log: 3", C1_PATTERN_HINT)

    names = {"  tuesday   log.log": log(MISSING, INDEX, FAVICON),
             "[ab].log": log(MISSING),
             "a.log": log(MISSING, FAVICON, ROBOTS, OLD_PAGE),
             "day=monday.log": log(OLD_PAGE, MONDAY_INDEX),
             "empty.log": ""}
    check_c1(["  tuesday   log.log", "[ab].log", "day=monday.log", "empty.log"], names,
             text("  tuesday   log.log: 2", "[ab].log: 1", "day=monday.log: 1", "empty.log: 0"),
             C1_NAMES_HINT)

    check_keeps_variables(C1, "report_404", "access.log", "monday log.log", files=files)


# c2


C2_ACCESS = log(INDEX, ERRORS_503, STATS, FAVICON)
C2_CLEAN = log(INDEX, ERRORS_503)

C2_FIRST_HINT = ('When grep -q " [45][0-9][0-9] " "$1" succeeds, print only the first matching '
                 "line, unchanged, with grep ... | head -n 1, and return 0.")
C2_NONE_HINT = ('Test for a failed request with grep -q " [45][0-9][0-9] " "$1" first, as '
                "healthcheck.sh does, and return 1 when it finds none. A pipeline such as "
                "grep ... | head -n 1 ends with head's status, 0 even when grep found nothing.")
C2_PATTERN_HINT = ('Match the status field only, with the pattern " [45][0-9][0-9] ", a space on '
                   "each side: a path such as /orders/451, or bytes such as 512 at the end of "
                   "the line, has no space on one side.")
C2_NAMES_HINT = ('Put $1 in double quotes wherever you use it: "$1" keeps a name with spaces in '
                 "one piece, and its * ? [ ] as plain text instead of a glob that can match "
                 "other files, such as 1.log.")
C2_FILE_HINT = ('First test [[ ! -f $1 ]]: -f is true only for a regular file, so a folder or a '
                'missing path gets the message, printed to stderr with >&2, and return 2.')
C2_RETURN_HINT = ("Use return, not exit: exit ends the whole script that called first_error, "
                  "so the commands after the call never run.")


def check_c2(name, files, expected, status, hint, stderr=""):
    run = call(C2, "first_error", name, files=files)
    problem = C2_NAMES_HINT if split_name(run, name) else None
    check_run(run, expected, status=status, stderr=stderr, hint=hint, problem=problem)


def check_c2_missing(name, files):
    check_c2(name, files, "", 2, C2_FILE_HINT, stderr=f"first_error: no such file: {name}")


def check_c2_goes_on(name, files, expected):
    run = in_shell(C2, f"first_error {name}", 'echo "status: $?"', files=files,
                   functions=["first_error"])
    stderr = "first_error: no such file: missing.log" if name == "missing.log" else ""
    check_run(run, expected, stderr=stderr, hint=C2_RETURN_HINT)


@pytest.mark.objective(2)
def test_c2_gives_back_the_first_failed_request():
    access = {"access.log": C2_ACCESS, "clean.log": C2_CLEAN}
    check_c2("access.log", access, STATS, 0, C2_FIRST_HINT)
    check_c2("clean.log", access, "", 1, C2_NONE_HINT)
    check_c2("empty.log", {"empty.log": ""}, "", 1, C2_NONE_HINT)
    check_c2("monday.log", {"monday.log": log(INDEX, ORDER_451, MISSING, UPLOAD)}, MISSING, 0,
             C2_PATTERN_HINT)
    check_c2("  monday   [1].log",
             {"  monday   [1].log": log(INDEX, STATS, MISSING), "1.log": log(MISSING)},
             STATS, 0, C2_NAMES_HINT)

    check_c2_missing("missing.log", access)
    check_c2_missing("logs", {"logs/monday.log": log(MONDAY_INDEX, OLD_PAGE)})
    check_c2_missing(" no such  [1].log", {"1.log": log(MISSING)})

    check_c2_goes_on("missing.log", access, "status: 2")
    check_c2_goes_on("clean.log", access, "status: 1")
    check_c2_goes_on("access.log", access, text(STATS, "status: 0"))


# c3


# 16 requests: 8 from C, 4 from B in a row, 3 from A and 1 from D.
RUNS = log_of("CBBBBCACDCACCACC")
RUNS_ABOUT = {"access.log": (
    f"access.log held 16 requests: 8 from {IPS['C']}, spread through the file, 4 in a row from "
    f"{IPS['B']}, 3 from {IPS['A']} and 1 from {IPS['D']}.")}

# 20 requests, the IPs mixed together: 10 from A, the rest fewer than 10 each.
BUSY = log_of("CABADAEBACABADCABAAA")
BUSY_ABOUT = {"access.log": (
    "access.log held 20 requests, the ones from each IP spread through the file: "
    f"10 from {IPS['A']}, 4 from {IPS['B']}, 3 from {IPS['C']}, 2 from {IPS['D']} "
    f"and 1 from {IPS['E']}.")}

C3_HINT = ('Make set -euo pipefail the first command, then ip=$(cut -d " " -f 2 "$1" | sort | '
           "uniq -c | sort -nr | sed -n 1p | awk '{ print $2 }'), then echo \"$1: busiest client "
           '$ip".')
C3_SORT_FIRST_HINT = ("uniq -c counts only repeated lines that are next to each other. Sort the "
                      "IPs before uniq -c, so the requests of each IP come together.")
C3_NUMBERS_HINT = ("Sort the counts as numbers, biggest first, with sort -nr, then keep the first "
                   "line with sed -n 1p.")
C3_NAMES_HINT = ('Put $1 in double quotes wherever you use it: "$1" keeps a name with spaces in '
                 "one piece, its runs of spaces too, and its * ? [ ] as plain text.")
C3_STOP_HINT = ("Let set -e and pipefail stop the script: capture the pipeline's output with "
                "ip=$( ... ) on a line of its own, then echo. With pipefail, cut's failure makes "
                "the assignment fail, and set -e stops before echo. Inside echo's arguments, or "
                "without pipefail, the failure goes unseen.")
C3_STATUS_HINT = ("Exit with cut's status, 1, by letting set -e stop the script: don't check "
                  "LOGFILE yourself, and don't exit with a status of your own.")
C3_MESSAGE_HINT = ("Let cut report the missing file on stderr: don't check LOGFILE yourself, and "
                   "don't send cut's errors to /dev/null.")


def check_c3(name, files, ip, hint, about=None):
    run = run_script(C3, name, files=files)
    problem = C3_NAMES_HINT if split_name(run, name) else None
    check_run(run, f"{name}: busiest client {ip}", hint=hint, about=about, problem=problem)


def check_c3_missing(name, files):
    run = run_script(C3, name, files=files)
    check_run(run, "", status=1, stderr=None, hint=C3_STOP_HINT, status_hint=C3_STATUS_HINT)
    if not lines(run.stderr):
        fail(given_files(run) + f"`{run.command}` should let cut print its error message to "
             "stderr, but printed nothing to stderr.", C3_MESSAGE_HINT)


@pytest.mark.objective(4)
def test_c3_prints_the_busiest_client_or_stops():
    check_c3("access.log", {"access.log": log(INDEX, MISSING, ABOUT)}, IPS["A"], C3_HINT)
    check_c3("access.log", {"access.log": RUNS}, IPS["C"], C3_SORT_FIRST_HINT, RUNS_ABOUT)
    check_c3("access.log", {"access.log": BUSY}, IPS["A"], C3_NUMBERS_HINT, BUSY_ABOUT)
    check_c3("  monday   [1].log",
             {"  monday   [1].log": log(MONDAY_INDEX, OLD_PAGE, FAVICON, ABOUT, MISSING, ROBOTS),
              "1.log": log(MONDAY_INDEX)},
             IPS["C"], C3_NAMES_HINT)

    check_c3_missing("missing.log", {"access.log": log(INDEX, MISSING, ABOUT)})
    check_c3_missing("logs/missing.log", {"logs/monday.log": log(MONDAY_INDEX, OLD_PAGE)})
    check_c3_missing(" no such  [1].log", {"1.log": log(MONDAY_INDEX)})
