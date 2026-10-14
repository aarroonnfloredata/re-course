"""Tests for exercise/loglib.sh and exercise/logkit.sh.

The other scripts in exercise/ are the finished tools of modules 1 to 10,
carried over unchanged, so they have no tests here.
"""

import shlex

import pytest

from checks import (IPS, check_keeps_variables, check_run, in_shell, log, log_of, split_name,
                    text)
from helpers import MODULE_DIR, call, execute, run_script

LOGLIB = "exercise/loglib.sh"
LOGKIT = "exercise/logkit.sh"

# Requests from the examples in loglib.sh and logkit.sh.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
ABOUT = "2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048"
ABOUT_404 = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
ERRORS_404 = "2026-10-06T10:16:48 203.0.113.5 GET /errors/404.html 200 1024"  # 404 in the path
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
STATS = "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"
ERRORS_503 = "2026-10-06T10:16:48 203.0.113.5 GET /errors/503.html 200 1024"  # 503 in the path
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"

# More requests.
CODES_404 = "2026-10-06T10:17:30 192.0.2.44 GET /codes/404 200 64"  # the path ends in 404
REDIRECT = "2026-10-06T10:18:10 192.0.2.44 GET /redirect/200 301 200"  # 200 in path and bytes
CODES_503 = "2026-10-06T10:18:20 10.0.0.8 GET /codes/503 200 64"  # the path ends in 503
LOGO_500 = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 500"  # 500 as the bytes
FORM = "2026-10-06T10:18:45 192.0.2.44 POST /form 502 64"

# The log of the examples in loglib.sh, and its ranking.
LIB_EXAMPLE = log(INDEX, MISSING, ABOUT, ABOUT_404, ERRORS_404, FAVICON)
LIB_RANKING = [(IPS["A"], 3), (IPS["C"], 2), (IPS["E"], 1)]

# The log of the examples in logkit.sh, and its ranking.
KIT_EXAMPLE = log(INDEX, MISSING, ABOUT, STATS, ERRORS_503, UPLOAD)
KIT_RANKING = [(IPS["A"], 3), (IPS["C"], 2), (IPS["E"], 1)]
MONDAY = log(MONDAY_INDEX, OLD_PAGE)

# A status in other fields: 404 in the path, at the end of the path and as
# the bytes; 200 at the end of the path and as the bytes; 153 as the bytes.
DECOYS = log(INDEX, ERRORS_404, ABOUT_404, CODES_404, MISSING, REDIRECT, FAVICON)

# 15 requests: 12 with status 404, 3 with status 200.
MANY = log(*(f"2026-10-06T10:{20 + minute:02d}:05 198.51.100.7 GET /old/{minute}.html 404 153"
             for minute in range(12)), INDEX, ABOUT, ERRORS_404)
MANY_ABOUT = {"access.log": "access.log held 15 requests: 12 with status 404 and 3 with "
                            "status 200."}

# 20 requests, the IPs mixed together: 10 from A, the rest fewer than 10 each.
BUSY = log_of("CABADAEBACABADCABAAA")
BUSY_RANKING = [(IPS["A"], 10), (IPS["B"], 4), (IPS["C"], 3), (IPS["D"], 2), (IPS["E"], 1)]
BUSY_ABOUT = {"access.log": (
    "access.log held 20 requests, the ones from each IP spread through the file: "
    f"10 from {IPS['A']}, 4 from {IPS['B']}, 3 from {IPS['C']}, 2 from {IPS['D']} "
    f"and 1 from {IPS['E']}.")}

# 16 requests: 8 from C, spread through the file, and 4 in a row from B.
RUNS = log_of("CBBBBCACDCACCACC")
RUNS_RANKING = [(IPS["C"], 8), (IPS["B"], 4), (IPS["A"], 3), (IPS["D"], 1)]
RUNS_ABOUT = {"access.log": (
    f"access.log held 16 requests: 8 from {IPS['C']}, spread through the file, 4 in a row from "
    f"{IPS['B']}, 3 from {IPS['A']} and 1 from {IPS['D']}.")}

# Short descriptions of the logs, for tests where their lines don't matter.
KIT_ABOUT = {
    "access.log": "access.log held the 6 requests of the examples in logkit.sh.",
    "monday log.log": "monday log.log held the 2 requests of the examples in logkit.sh.",
    "logs/monday.log": "logs/monday.log, in the folder logs, held 2 requests.",
    "a.log": "a.log held 1 request.",
}

USAGE = "logkit: usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE"


def ranked(ranking, n):
    """The lines top_clients prints: the first `n` of `ranking`."""
    return text(*(f"{ip} {count}" for ip, count in ranking[:n]))


def names_hint(variable):
    return (f'Put {variable} in double quotes wherever you use it. Quoted, a name keeps its runs '
            "of spaces, and its * ? [ ] are plain text. Unquoted, a name is split at its "
            "spaces, and * ? [ ] make a glob that can match other files, such as a.log.")


# count_status


COUNT_HINT = ('Count with grep -c " $status " "$logfile": it prints the number by itself. '
              "Print nothing else.")
COUNT_PATTERN_HINT = ('Count the lines that contain STATUS with a space on each side, " $status ": '
                      "a status in the path, or as the bytes at the end of the line, has no "
                      "space on one side.")
COUNT_FOUND_STATUS_HINT = ("Return status 0 when the count is 1 or more: make grep -c the "
                           "function's last command, and its status becomes the function's.")
COUNT_NONE_HINT = ("When no request has STATUS, print 0 and return status 1, as grep -c does. "
                   "Make grep -c the function's last command, so that its status becomes the "
                   "function's: a command after it, such as echo, gives back its own status, "
                   "0. So does local n=$(...).")
COUNT_DIGITS_HINT = ("Print the number as digits only. grep -c prints it that way; wc -l on "
                     "macOS puts spaces before it.")
ARGUMENTS_HINT = "LOGFILE is the first argument, $1, and STATUS the second, $2."


def count_problem(run, status):
    """A hint for a mistake the run shows whatever the test is about."""
    if f"{status}: No such file" in run.stderr:
        return ARGUMENTS_HINT
    if split_name(run, *run.given):
        return names_hint("$logfile")
    return None


def call_count(name, status, files):
    return call(LOGLIB, "count_status", name, status, files=files)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize("status, count", [("404", 2), ("200", 4)])
def test_count_status_prints_the_count(status, count):
    run = call_count("access.log", status, {"access.log": LIB_EXAMPLE})
    check_run(run, str(count), hint=COUNT_HINT, status_hint=COUNT_FOUND_STATUS_HINT,
              problem=count_problem(run, status))


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize("status, count", [("404", 2), ("200", 4), ("301", 1)])
def test_count_status_counts_only_the_status_field(status, count):
    run = call_count("access.log", status, {"access.log": DECOYS})
    check_run(run, str(count), hint=COUNT_PATTERN_HINT, status_hint=COUNT_FOUND_STATUS_HINT,
              problem=count_problem(run, status))


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "name, log_text, status",
    [
        ("access.log", LIB_EXAMPLE, "500"),
        ("empty day.log", "", "404"),
        ("access.log", log(INDEX, ERRORS_404, ABOUT_404, CODES_404), "404"),
        ("access.log", DECOYS, "153"),
    ],
    ids=["example-500", "empty-file", "404-only-in-other-fields", "153-only-as-bytes"],
)
def test_count_status_prints_0_and_returns_1_when_there_are_none(name, log_text, status):
    run = call_count(name, status, {name: log_text})
    check_run(run, "0", status=1, hint=COUNT_PATTERN_HINT, status_hint=COUNT_NONE_HINT,
              problem=count_problem(run, status))


@pytest.mark.objective(2)
@pytest.mark.parametrize("status, count", [("404", 12), ("200", 3)])
def test_count_status_prints_counts_past_nine(status, count):
    run = call_count("access.log", status, {"access.log": MANY})
    check_run(run, str(count), hint=COUNT_DIGITS_HINT, status_hint=COUNT_FOUND_STATUS_HINT,
              about=MANY_ABOUT, problem=count_problem(run, status))


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "name", ["monday log.log", "  tuesday   log.log", "[ab].log", "status=404.log",
             "logs/monday.log"])
def test_count_status_reads_any_file_name(name):
    run = call_count(name, "404", {name: log(MISSING, INDEX, FAVICON), "a.log": log(MISSING)})
    check_run(run, "2", hint=names_hint("$logfile"), status_hint=COUNT_FOUND_STATUS_HINT,
              problem=count_problem(run, "404"))


@pytest.mark.objective(1)
def test_count_status_keeps_its_variables_local():
    check_keeps_variables(LOGLIB, "count_status", "access.log", "404",
                          files={"access.log": LIB_EXAMPLE})


# top_clients


TOP_HINT = ('Rank with the pipeline of top.sh, keeping the first N lines with sed -n "1,${n}p": '
            'cut -d " " -f 2 "$logfile" | sort | uniq -c | sort -nr | sed -n "1,${n}p" | '
            'while read -r count ip; do echo "$ip $count"; done.')
TOP_N_HINT = ('sed -n "1,${n}p" prints lines 1 to N, and all of them when there are fewer: '
              "after sort -nr, those are the N IPs with the most requests.")
TOP_SORT_HINT = ("uniq -c counts only repeated lines that are next to each other: sort the IPs "
                 "before uniq -c. Then sort the counts as numbers, biggest first, with sort -nr.")
TOP_EMPTY_HINT = ("An empty file gives the pipeline no lines, so it prints nothing. Print nothing "
                  "else, not even an empty line, and return status 0.")
TOP_STATUS_HINT = ("Return status 0: make the pipeline the function's last command, and its "
                   "status, that of the while loop, becomes the function's.")
TOP_WORD_HINT = ("Don't check N yourself: let sed fail, and make the pipeline the last command "
                 "of top_clients, with no return after it. Without pipefail, the pipeline's "
                 "status is that of its last command, the while loop: 0.")
TOP_PIPEFAIL_HINT = ("Make the pipeline the last command of top_clients, with no return or "
                     "other command after it, so that the function returns the pipeline's "
                     "status. Under pipefail, that is sed's status, 1.")


def check_top(name, n, files, ranking, hint, about=None):
    run = call(LOGLIB, "top_clients", name, str(n), files=files)
    problem = names_hint("$logfile") if split_name(run, name) else None
    check_run(run, ranked(ranking, n), hint=hint, status_hint=TOP_STATUS_HINT, about=about,
              problem=problem)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize("n", [2, 1, 3, 5])
def test_top_clients_ranks_the_example(n):
    check_top("access.log", n, {"access.log": LIB_EXAMPLE}, LIB_RANKING, TOP_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize("n", [1, 2, 4, 5, 6, 12])
def test_top_clients_keeps_the_n_ips_with_the_most_requests(n):
    check_top("access.log", n, {"access.log": BUSY}, BUSY_RANKING, TOP_N_HINT, BUSY_ABOUT)


@pytest.mark.objective(2)
@pytest.mark.parametrize("n", [1, 2, 4])
def test_top_clients_counts_all_requests_of_each_ip(n):
    check_top("access.log", n, {"access.log": RUNS}, RUNS_RANKING, TOP_SORT_HINT, RUNS_ABOUT)


@pytest.mark.objective(2)
def test_top_clients_prints_nothing_for_an_empty_file():
    check_top("empty day.log", 3, {"empty day.log": ""}, [], TOP_EMPTY_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "name", ["monday log.log", "  tuesday   log.log", "[ab].log", "status=404.log",
             "logs/monday.log"])
def test_top_clients_reads_any_file_name(name):
    check_top(name, 2, {name: LIB_EXAMPLE, "a.log": log(MONDAY_INDEX)}, LIB_RANKING,
              names_hint("$logfile"))


@pytest.mark.objective(2, 4)
def test_top_clients_returns_0_for_a_word_without_pipefail():
    run = in_shell(LOGLIB, "top_clients access.log abc", 'echo "top_clients returned $?"',
                   files={"access.log": LIB_EXAMPLE}, functions=["top_clients"])
    check_run(run, "top_clients returned 0", stderr=None, hint=TOP_WORD_HINT)


@pytest.mark.objective(2, 4)
def test_top_clients_returns_1_for_a_word_under_pipefail():
    run = in_shell(LOGLIB, "set -o pipefail", "top_clients access.log abc",
                   'echo "top_clients returned $?"', files={"access.log": LIB_EXAMPLE},
                   functions=["top_clients"])
    check_run(run, "top_clients returned 1", stderr=None, hint=TOP_PIPEFAIL_HINT)


@pytest.mark.objective(1)
def test_top_clients_keeps_its_variables_local():
    check_keeps_variables(LOGLIB, "top_clients", "access.log", "2",
                          files={"access.log": LIB_EXAMPLE})


# die


DIE_HINT = ('Print the line to stderr, with $1 in double quotes: echo "logkit: $1" >&2. Quoted, '
            "the message keeps its runs of spaces, and its * ? [ ] are plain text.")
DIE_STATUS_HINT = "End with exit 2: exit ends the script with that status."
DIE_EXIT_HINT = ("Use exit 2, not return: exit ends the whole script, also when die is called "
                 "from inside another function. return ends only die, and the commands after "
                 "the call still run.")


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "message, files",
    [
        ("no such file: monday  log.log", None),
        ("  stop   here", None),
        ("usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE", None),
        ("no log matches *.log or [ab]?.log", {"a.log": "", "ab.log": "", "monday.log": ""}),
        ("cost: $5; total=$total \"double\" 'single'", None),
    ],
    ids=["double-space", "leading-spaces", "usage", "glob", "dollar-quotes"],
)
def test_die_prints_the_message_to_stderr(message, files):
    run = call(LOGLIB, "die", message, files=files)
    check_run(run, "", status=2, stderr=f"logkit: {message}", hint=DIE_HINT,
              status_hint=DIE_STATUS_HINT)


@pytest.mark.objective(2)
def test_die_ends_the_script():
    run = in_shell(LOGLIB, 'die "stop here"', 'echo "after die"', functions=["die"])
    check_run(run, "", status=2, stderr="logkit: stop here", hint=DIE_EXIT_HINT)


@pytest.mark.objective(2)
def test_die_ends_the_script_from_inside_a_function():
    run = in_shell(LOGLIB,
                   'check_log() { die "no such file: missing.log"; echo "after die, in check_log"; }',
                   "check_log", 'echo "after check_log"', functions=["die"])
    check_run(run, "", status=2, stderr="logkit: no such file: missing.log", hint=DIE_EXIT_HINT)


# logkit.sh


LIBRARY_HINT = ('Load loglib.sh from the folder logkit.sh is in: source "$(dirname "$0")/loglib.sh". '
                "The tests run logkit.sh from another folder, where there is no loglib.sh.")
UNBOUND_HINT = ("Under set -u, reading an argument that wasn't given stops logkit: check $# "
                "before you read $1, $2 or $3.")
KIT_COUNT_HINT = ('Capture the count with n=$(count_status "$2" "$3"), then print '
                  '"$2: $n requests with status $3".')
KIT_COUNT_NONE_HINT = ("Capture the count with n=$(count_status ...) on a line of its own, before "
                       "echo: when count_status returns 1, the assignment fails with 1 and "
                       "set -e stops logkit before the line is printed. Inside echo's arguments, "
                       "echo's status, 0, hides it.")
KIT_TOP_HINT = 'Run top_clients "$2" "$3" and let it print its lines.'
KIT_TOP_WORD_HINT = ("Make set -euo pipefail logkit's first command, and don't check N yourself: "
                     "with pipefail, top_clients returns sed's status, 1, and set -e stops "
                     "logkit with it.")
KIT_HEALTH_HINT = ('When if grep -q " 5[0-9][0-9] " "$2" succeeds, print the matching lines with '
                   'grep " 5[0-9][0-9] " "$2" and exit with 1.')
KIT_HEALTH_NONE_HINT = ('Test for 5xx requests with if grep -q " 5[0-9][0-9] " "$2": set -e '
                        "ignores a command that if tests. A grep that finds nothing on a line of "
                        'its own stops logkit with 1, before it prints "LOGFILE: no 5xx errors".')
KIT_USAGE_HINT = ("Check the arguments before anything else: when $# is 0, when $1 is not count, "
                  "top or health, or when the number of arguments after it is wrong, call die "
                  "with the usage message. die adds logkit: and exits with 2.")
KIT_NAMES_HINT = ('Put LOGFILE in double quotes wherever you use it, "$2" or "$logfile". Quoted, a '
                  "name keeps its runs of spaces, and its * ? [ ] are plain text. Inside "
                  "[[ ]] it needs no quotes; inside [ ] it does.")
KIT_FILE_HINT = ('After the usage check, test the file with [[ ! -f $2 ]]: -f is true only for a '
                 'regular file, so a folder or a missing path gets die "no such file: $2".')


def logkit_problem(run, *names):
    """A hint for a mistake the run shows whatever the test is about."""
    if "loglib.sh: No such file" in run.stderr:
        return LIBRARY_HINT
    if "unbound variable" in run.stderr:
        return UNBOUND_HINT
    if split_name(run, *names):
        return KIT_NAMES_HINT
    return None


def check_logkit(args, files, stdout, status=0, stderr="", hint=None, status_hint=None,
                 about=None):
    run = run_script(LOGKIT, *args, files=files)
    check_run(run, stdout, status=status, stderr=stderr, hint=hint, status_hint=status_hint,
              about=about, problem=logkit_problem(run, *args[1:2]))


@pytest.mark.objective(2, 3)
@pytest.mark.parametrize(
    "name, status, files, expected",
    [
        ("access.log", "200", {"access.log": KIT_EXAMPLE}, 3),
        ("access.log", "503", {"access.log": KIT_EXAMPLE}, 1),
        ("monday log.log", "404", {"monday log.log": MONDAY}, 1),
        ("access.log", "404", {"access.log": MANY}, 12),
        ("  tuesday   log.log", "404", {"  tuesday   log.log": DECOYS}, 2),
        ("[ab].log", "200", {"[ab].log": KIT_EXAMPLE, "a.log": log(INDEX)}, 3),
        ("logs/monday.log", "404", {"logs/monday.log": MONDAY}, 1),
    ],
    ids=["example-200", "example-503", "monday", "twelve", "spaces", "glob", "subfolder"],
)
def test_logkit_count_prints_the_count(name, status, files, expected):
    about = MANY_ABOUT if files.get("access.log") == MANY else None
    check_logkit(["count", name, status], files,
                 f"{name}: {expected} requests with status {status}", hint=KIT_COUNT_HINT,
                 about=about)


@pytest.mark.objective(2, 4)
@pytest.mark.parametrize(
    "name, status, files",
    [
        ("access.log", "401", {"access.log": KIT_EXAMPLE}),
        ("access.log", "404", {"access.log": log(INDEX, ERRORS_404, ABOUT_404, CODES_404)}),
        ("empty.log", "500", {"empty.log": ""}),
    ],
    ids=["example-401", "404-only-in-other-fields", "empty-file"],
)
def test_logkit_count_prints_nothing_and_exits_with_1_when_there_are_none(name, status, files):
    check_logkit(["count", name, status], files, "", status=1, hint=KIT_COUNT_NONE_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "name, n, files, ranking, about",
    [
        ("access.log", 2, {"access.log": KIT_EXAMPLE}, KIT_RANKING, None),
        ("access.log", 10, {"access.log": KIT_EXAMPLE}, KIT_RANKING, None),
        ("access.log", 3, {"access.log": BUSY}, BUSY_RANKING, BUSY_ABOUT),
        ("  tuesday   log.log", 1, {"  tuesday   log.log": KIT_EXAMPLE}, KIT_RANKING, None),
        ("empty day.log", 3, {"empty day.log": ""}, [], None),
    ],
    ids=["example-2", "example-10", "busy-3", "spaces", "empty-file"],
)
def test_logkit_top_prints_the_ranking(name, n, files, ranking, about):
    check_logkit(["top", name, str(n)], files, ranked(ranking, n), hint=KIT_TOP_HINT,
                 about=about)


@pytest.mark.objective(4)
@pytest.mark.parametrize("name, n, files", [
    ("access.log", "abc", {"access.log": KIT_EXAMPLE}),
    ("monday log.log", "xyz", {"monday log.log": MONDAY}),
], ids=["abc", "xyz"])
def test_logkit_top_stops_with_1_for_a_word(name, n, files):
    check_logkit(["top", name, n], files, "", status=1, stderr=None, hint=KIT_TOP_WORD_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "name, files, expected",
    [
        ("access.log", {"access.log": KIT_EXAMPLE}, text(STATS, UPLOAD)),
        ("  tuesday   log.log", {"  tuesday   log.log": log(UPLOAD, INDEX, FORM, MISSING)},
         text(UPLOAD, FORM)),
    ],
    ids=["example", "spaces"],
)
def test_logkit_health_prints_the_5xx_requests_and_exits_with_1(name, files, expected):
    check_logkit(["health", name], files, expected, status=1, hint=KIT_HEALTH_HINT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "name, files",
    [
        ("monday log.log", {"monday log.log": MONDAY}),
        ("empty.log", {"empty.log": ""}),
        ("decoys.log", {"decoys.log": log(ERRORS_503, CODES_503, LOGO_500, INDEX)}),
        ("[ab].log", {"[ab].log": log(INDEX), "a.log": log(STATS)}),
    ],
    ids=["monday", "empty-file", "5xx-only-in-other-fields", "glob"],
)
def test_logkit_health_reports_no_5xx_errors(name, files):
    check_logkit(["health", name], files, f"{name}: no 5xx errors", hint=KIT_HEALTH_NONE_HINT)


@pytest.mark.objective(3, 4)
@pytest.mark.parametrize(
    "args",
    [
        [],
        ["list", "access.log"],
        ["", "access.log", "200"],
        ["COUNT", "access.log", "200"],
        ["count"],
        ["count", "access.log"],
        ["count", "access.log", "200", "404"],
        ["top", "access.log"],
        ["top", "access.log", "2", "3"],
        ["health"],
        ["health", "access.log", "monday log.log"],
        ["count", "missing.log"],
        ["health", "missing.log", "logs"],
    ],
    ids=["no-arguments", "list", "empty-subcommand", "upper-case", "count-alone",
         "count-one", "count-three", "top-one", "top-three", "health-alone", "health-two",
         "count-missing-one", "health-missing-two"],
)
def test_logkit_prints_the_usage_for_wrong_arguments(args):
    files = {"access.log": KIT_EXAMPLE, "monday log.log": MONDAY}
    check_logkit(args, files, "", status=2, stderr=USAGE, hint=KIT_USAGE_HINT, about=KIT_ABOUT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "args, name",
    [
        (["count", "missing.log", "404"], "missing.log"),
        (["top", "missing.log", "3"], "missing.log"),
        (["top", "missing.log", "abc"], "missing.log"),
        (["health", "logs"], "logs"),
        (["count", "logs", "404"], "logs"),
        (["health", "  no such   log.log"], "  no such   log.log"),
        (["health", "[ab].log"], "[ab].log"),
    ],
    ids=["count", "top", "top-word", "health-folder", "count-folder", "spaces", "glob"],
)
def test_logkit_stops_when_the_file_is_missing(args, name):
    files = {"access.log": KIT_EXAMPLE, "logs/monday.log": MONDAY, "a.log": log(INDEX)}
    check_logkit(args, files, "", status=2, stderr=f"logkit: no such file: {name}",
                 hint=KIT_FILE_HINT, about=KIT_ABOUT)


# A loglib.sh for the next test, to see which functions logkit.sh calls.
TEST_LIBRARY = """\
count_status() {
    echo 7
}
top_clients() {
    echo "top_clients was called with $1 and $2"
}
die() {
    echo "die was called with: $1" >&2
    exit 3
}
"""
TEST_LIBRARY_ABOUT = {
    "tools/logkit.sh": "tools/logkit.sh was a copy of exercise/logkit.sh.",
    "tools/loglib.sh": ("tools/loglib.sh was a loglib.sh written for this test: its count_status "
                        'prints 7, its top_clients prints "top_clients was called with LOGFILE '
                        'and N", and its die prints "die was called with: MESSAGE" to stderr '
                        "and exits with 3."),
}
TEST_LIBRARY_HINT = ('logkit.sh should load the loglib.sh in its own folder, with source '
                     '"$(dirname "$0")/loglib.sh", and use its functions: count_status for '
                     "count, top_clients for top, and die for every error, instead of doing "
                     "their work itself.")
USAGE_MESSAGE = "usage: logkit.sh count LOGFILE STATUS | top LOGFILE N | health LOGFILE"


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "args, stdout, stderr, status",
    [
        (["count", "access.log", "200"], "access.log: 7 requests with status 200", "", 0),
        (["top", "access.log", "2"], "top_clients was called with access.log and 2", "", 0),
        ([], "", f"die was called with: {USAGE_MESSAGE}", 3),
        (["count", "access.log"], "", f"die was called with: {USAGE_MESSAGE}", 3),
        (["health", "missing.log"], "", "die was called with: no such file: missing.log", 3),
    ],
    ids=["count", "top", "usage", "count-one", "missing-file"],
)
def test_logkit_uses_the_functions_of_the_loglib_next_to_it(args, stdout, stderr, status):
    logkit = MODULE_DIR / LOGKIT
    if not logkit.is_file():
        pytest.fail(f"There is no {LOGKIT}.", pytrace=False)
    files = {"access.log": KIT_EXAMPLE, "tools/logkit.sh": logkit.read_text(),
             "tools/loglib.sh": TEST_LIBRARY}
    command = ["bash", "tools/logkit.sh", *args]
    run = execute(command, shlex.join(command), "", files)
    check_run(run, stdout, status=status, stderr=stderr, hint=TEST_LIBRARY_HINT,
              about=TEST_LIBRARY_ABOUT, problem=logkit_problem(run))
