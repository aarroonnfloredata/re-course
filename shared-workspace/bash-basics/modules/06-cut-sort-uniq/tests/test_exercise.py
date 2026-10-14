"""Tests for exercise/top.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh,
exercise/healthcheck.sh and exercise/summary.sh are the finished tools of
modules 1 to 5, carried over unchanged, so they have no tests here.
"""

import re

import pytest

from checks import check_run, log, name_error, text
from helpers import lines, run_script

TOP = "exercise/top.sh"

# The log of the examples in top.sh.
EXAMPLE = log(
    "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
    "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    "2026-10-06T10:16:02 203.0.113.5 GET /about.html 200 2048",
    "2026-10-06T10:16:15 192.0.2.44 GET /index.html 200 512",
    "2026-10-06T10:16:48 203.0.113.5 GET /logo.png 200 4096",
    "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153",
)
EXAMPLE_RANKING = [("203.0.113.5", 3), ("198.51.100.7", 2), ("192.0.2.44", 1)]

IPS = {"A": "203.0.113.5", "B": "10.0.0.8", "C": "198.51.100.7", "D": "172.16.0.3",
       "E": "192.0.2.44"}
PATHS = ["/index.html", "/about.html", "/logo.png", "/api/stats", "/login", "/missing.html"]
STATUSES = [200, 200, 404, 200, 301, 500, 401]
SIZES = [512, 2048, 4096, 0, 153, 64]


def request(position, ip):
    """The request on line `position` (from 0) of a made-up log, from `ip`."""
    seconds = 15 * 60 + 11 * position
    time = f"2026-10-06T10:{seconds // 60:02d}:{seconds % 60:02d}"
    method = "POST" if position % 5 == 3 else "GET"
    path, status, size = (PATHS[position % len(PATHS)], STATUSES[position % len(STATUSES)],
                          SIZES[position % len(SIZES)])
    return f"{time} {ip} {method} {path} {status} {size}"


def log_of(letters):
    """A log whose lines come from the IPs that `letters` name, in that order."""
    return log(*(request(position, IPS[letter]) for position, letter in enumerate(letters)))


# 20 requests: the IPs mixed together, counts of 10 and of one digit.
BUSY = log_of("CABADAEBACABADCABAAA")
BUSY_RANKING = [(IPS["A"], 10), (IPS["B"], 4), (IPS["C"], 3), (IPS["D"], 2), (IPS["E"], 1)]
BUSY_ABOUT = {"access.log": (
    "access.log held 20 requests, the ones from each IP spread through the file: "
    f"10 from {IPS['A']}, 4 from {IPS['B']}, 3 from {IPS['C']}, 2 from {IPS['D']} "
    f"and 1 from {IPS['E']}.")}

# Every IP's requests apart from each other.
APART = log_of("EAEAEBEAE")
APART_RANKING = [(IPS["E"], 5), (IPS["A"], 3), (IPS["B"], 1)]

# 12 requests from one IP.
ONE_IP = log_of("C" * 12)
ONE_IP_RANKING = [(IPS["C"], 12)]
ONE_IP_ABOUT = {"access.log": f"access.log held 12 requests, all from {IPS['C']}."}

NOTES = log("Look into the 404s.")

LINE = re.compile(r"^(\S+) (\S+)$")

EXAMPLE_HINT = ('"Ranking with one pipeline" in lesson.md ranks the paths of a log. top.sh '
                "ranks the client IPs, the second field, prints only the N IPs with the most "
                "requests, and prints each as IP COUNT.")
TOP_N_HINT = ('head -n "$2" keeps the first N lines. Put it after sort -nr, so those lines '
              "hold the biggest counts.")
ALL_HINT = ("When LOGFILE holds N IPs or fewer, head -n N keeps every line: print them all, "
            "the biggest count first.")
EMPTY_HINT = ('Read the file the first argument names, "$1", whatever its name. An empty file '
              "gives the pipeline no lines, so it prints nothing.")
SORT_FIRST_HINT = ("uniq -c counts only repeated lines that are next to each other. Sort the "
                   "IPs before uniq -c, so the requests of each IP come together.")
PADDED_HINT = ("uniq -c puts spaces before each count, and how many depends on the system. End "
               "the pipeline with while read -r count ip, which drops them, and print "
               '"$ip $count".')
SPACING_HINT = ("Print one space between the IP and its count, and no other spaces: "
                'echo "$ip $count".')
SWAPPED_HINT = ("Print the IP first, then its count: uniq -c puts the count first, so "
                'read -r count ip and print "$ip $count".')
COUNT_ALL_HINT = ("Each count is the number of the IP's requests in the whole file: uniq -c "
                  "must see every request, so nothing that drops lines, such as head or "
                  "sort -u, can come before it.")
FIELD_HINT = "The client IP is the second field: cut -d ' ' -f 2."
ASCENDING_HINT = ("Biggest count first: sort -n puts the smallest number first, and -r turns "
                  "that around: sort -nr.")
NUMBERS_HINT = ("Sort the counts as numbers, biggest first, with sort -nr. Sorted as text, the "
                "order depends on the spaces uniq -c puts before each count.")
N_HINT = 'Print N lines, N being the second argument: head -n "$2".'
ARGUMENTS_HINT = 'LOGFILE is the first argument, "$1", and N the second, "$2".'
HEAD_HINT = ("head keeps whatever lines come first. Sort the lines of uniq -c with sort -nr "
             "before it, so the first lines hold the biggest counts.")


def spaces_hint(name):
    return (f'Put $1 in double quotes wherever you use it: "$1" keeps {name!r} in one piece, '
            "its runs of spaces too.")


def glob_hint(name, other):
    return (f"Put $1 in double quotes wherever you use it: quoted, the * ? [ ] in {name!r} are "
            f"plain text. Unquoted, they make a glob that can match other files, such as "
            f"{other}.")


def ranked(ranking):
    return [f"{ip} {count}" for ip, count in ranking]


def problem(run, ranking, n):
    """A hint for a mistake the run shows whatever the test is about."""
    if f": {n}: No such file" in run.stderr:
        return ARGUMENTS_HINT
    want, got = ranked(ranking[:n]), lines(run.stdout)
    if not want or not got or got == want:
        return None
    if any(not LINE.match(line) for line in got):
        if any(line[:1].isspace() for line in got):
            return PADDED_HINT
        if all(LINE.match(" ".join(line.split())) for line in got):
            return SPACING_HINT
        return None
    pairs = [LINE.match(line).groups() for line in got]
    counts = {ip: str(count) for ip, count in ranking}
    if all(first.isdigit() and second in counts for first, second in pairs):
        return SWAPPED_HINT
    if any(first not in counts for first, _ in pairs):
        return FIELD_HINT
    ips = [first for first, _ in pairs]
    if len(set(ips)) < len(ips):
        return SORT_FIRST_HINT
    if any(counts[ip] != count for ip, count in pairs):
        return COUNT_ALL_HINT
    numbers = [int(count) for _, count in pairs]
    smallest_first = ranked(sorted(ranking, key=lambda pair: pair[1]))
    if (len(got) > 1 and numbers == sorted(numbers)) or got == smallest_first[:len(got)]:
        return ASCENDING_HINT
    if numbers != sorted(numbers, reverse=True):
        return NUMBERS_HINT
    if len(got) != len(want) and got == ranked(ranking)[:len(got)]:
        return N_HINT
    if len(got) == len(want):
        return HEAD_HINT
    return None


def check_top(files, n, ranking, hint, about=None):
    """Run top.sh on access.log and fail unless it printed the first `n`
    lines of `ranking`, nothing to stderr, exited with 0 and left the files
    as they were."""
    run = run_script(TOP, "access.log", str(n), files=files)
    expected = text(*ranked(ranking[:n]))
    check_run(run, expected, hint, problem(run, ranking, n), about)


@pytest.mark.objective(1, 2, 3, 4)
@pytest.mark.parametrize("n", [2, 1, 5])
def test_ranks_the_example(n):
    check_top({"access.log": EXAMPLE, "notes.txt": NOTES}, n, EXAMPLE_RANKING, EXAMPLE_HINT)


@pytest.mark.objective(2, 4)
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_keeps_the_n_ips_with_the_most_requests(n):
    check_top({"access.log": BUSY}, n, BUSY_RANKING, TOP_N_HINT, BUSY_ABOUT)


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "log_text, n, ranking, about",
    [
        (EXAMPLE, 3, EXAMPLE_RANKING, None),
        (EXAMPLE, 10, EXAMPLE_RANKING, None),
        (BUSY, 5, BUSY_RANKING, BUSY_ABOUT),
        (BUSY, 6, BUSY_RANKING, BUSY_ABOUT),
        (BUSY, 12, BUSY_RANKING, BUSY_ABOUT),
    ],
    ids=["example-3", "example-10", "busy-5", "busy-6", "busy-12"],
)
def test_prints_every_ip_when_there_are_n_or_fewer(log_text, n, ranking, about):
    check_top({"access.log": log_text}, n, ranking, ALL_HINT, about)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "log_text, n, ranking, about",
    [
        (APART, 3, APART_RANKING, None),
        (APART, 2, APART_RANKING, None),
        (ONE_IP, 1, ONE_IP_RANKING, ONE_IP_ABOUT),
        (ONE_IP, 3, ONE_IP_RANKING, ONE_IP_ABOUT),
    ],
    ids=["apart-3", "apart-2", "one-ip-1", "one-ip-3"],
)
def test_counts_every_request_of_an_ip(log_text, n, ranking, about):
    check_top({"access.log": log_text}, n, ranking, SORT_FIRST_HINT, about)


@pytest.mark.objective(4)
@pytest.mark.parametrize("n", [1, 3])
def test_an_empty_log_prints_nothing(n):
    run = run_script(TOP, "empty.log", str(n), files={"empty.log": "", "access.log": EXAMPLE})
    check_run(run, "", EMPTY_HINT)


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "name, files, n, expected, hint",
    [
        ("monday  log.log", {"monday  log.log": log_of("AAB")}, 2,
         [f"{IPS['A']} 2", f"{IPS['B']} 1"], spaces_hint("monday  log.log")),
        ("  tuesday   log.log", {"  tuesday   log.log": log_of("CDC")}, 1,
         [f"{IPS['C']} 2"], spaces_hint("  tuesday   log.log")),
        ("logs/monday  log.log", {"logs/monday  log.log": log_of("ECEEC"), "access.log": EXAMPLE},
         3, [f"{IPS['E']} 3", f"{IPS['C']} 2"], spaces_hint("logs/monday  log.log")),
        ("*.log", {"*.log": log_of("AAB"), "access.log": log_of("BBBC")}, 2,
         [f"{IPS['A']} 2", f"{IPS['B']} 1"], glob_hint("*.log", "access.log")),
        ("day?.log", {"day?.log": log_of("ABA"), "day1.log": log_of("CCC")}, 2,
         [f"{IPS['A']} 2", f"{IPS['B']} 1"], glob_hint("day?.log", "day1.log")),
        ("[old].log", {"[old].log": log_of("ABB"), "o.log": log_of("AAAC")}, 2,
         [f"{IPS['B']} 2", f"{IPS['A']} 1"], glob_hint("[old].log", "o.log")),
    ],
    ids=["two-spaces-in-a-row", "spaces-at-the-start-and-in-a-row", "in-a-subfolder",
         "star-as-a-name", "question-mark-in-a-name", "brackets-in-a-name"],
)
def test_names_with_spaces_and_glob_characters(name, files, n, expected, hint):
    run = run_script(TOP, name, str(n), files=files)
    check_run(run, text(*expected), hint, spaces_hint(name) if name_error(run) else None)
