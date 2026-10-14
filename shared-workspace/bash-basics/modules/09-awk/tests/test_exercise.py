"""Tests for exercise/bytes.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh,
exercise/healthcheck.sh, exercise/summary.sh, exercise/top.sh,
exercise/suspicious.sh and exercise/anonymize.sh are the finished tools of
modules 1 to 8, carried over unchanged, so they have no tests here.
"""

import re

import pytest

from checks import check_run, glob_hint, log, name_error, spaces_hint
from helpers import lines, run_script

BYTES = "exercise/bytes.sh"

# The requests of the example in bytes.sh.
EXAMPLE = [
    "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
    "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0",
    "2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024",
    "2026-10-06T10:17:03 203.0.113.5 POST /login 401 64",
    "2026-10-06T10:17:45 192.0.2.44 GET /old.html 301 404",
]
CLEAN = [EXAMPLE[0], EXAMPLE[3]]

# Plain requests that tests put around the one they are about. Nothing in
# them looks like a status of 400 or more.
ABOUT = "2026-10-06T10:16:30 192.0.2.44 GET /about.html 200 2048"
HOME = "2026-10-06T10:18:10 198.51.100.7 GET /home 200 64"

NOTES = log("Look into the 404s.")


def request(status=200, size=512, path="/index.html", ip="203.0.113.5", method="GET",
            time="2026-10-06T10:17:20"):
    """A request, the one a test is about."""
    return f"{time} {ip} {method} {path} {status} {size}"


def monday(status, size, path="/index.html"):
    """A request from another day, for log files other than access.log."""
    return request(status, size, path, "192.0.2.44", time="2026-10-05T09:12:44")


def status_and_size(line):
    fields = line.split(" ")
    return int(fields[4]), int(fields[5])


def errors_sum(requests, counts):
    """The bytes of the requests for which `counts(status, size)` is true."""
    return sum(size for status, size in map(status_and_size, requests) if counts(status, size))


def failed(status, size):
    return status >= 400


def report(requests):
    """What bytes.sh prints for `requests`."""
    total = sum(size for _, size in map(status_and_size, requests))
    return [f"total: {total} bytes", f"errors: {errors_sum(requests, failed)} bytes"]


EXAMPLE_HINT = ("Add the bytes field, $6, of every request to one total, and of each request "
                "whose status, $5, is 400 or more to another. Print both in an END block.")
ZERO_HINT = ("A sum that no line added to is empty, not 0: print total + 0 and errors + 0 in "
             "END.")
NO_ERRORS_HINT = ("When no request failed, nothing is added to the errors sum and it stays "
                  "empty: print errors + 0.")
END_HINT = ("Print the two lines once, in an END block: a print in an action that runs for "
            "every line prints on every line.")
ORDER_HINT = "Print the total line first, then the errors line."
PLUS_HINT = "Add each request's bytes to the total with +=: = keeps only the last line's bytes."
TOTAL_HINT = ("The total counts every request, the failed ones too: give the action that adds "
              "to it no pattern.")
COMPARE_HINT = ("A request failed when its status, $5, is 400 or more: $5 >= 400 counts 400 "
                "and every 4xx and 5xx status, and nothing below 400.")
GREATER_HINT = "Status 400 counts too: use $5 >= 400, not $5 > 400."
FIVE_XX_HINT = "5xx statuses count too: every status of 400 or more failed, $5 >= 400."
FOUR_XX_HINT = "4xx statuses count too: every status of 400 or more failed, $5 >= 400."
FIELD_HINT = "The status is the fifth field: compare $5 >= 400. $6 and $NF are the bytes."
ONLY_STATUS_HINT = ("Only the status field decides: compare $5 >= 400. A pattern on the whole "
                    "line, such as / 4/ or /404/, also finds numbers in the path, the IP or the "
                    "bytes.")
LARGE_HINT = "Print each sum as a whole number, digits only, such as 1000000000."
ARGUMENT_HINT = 'Read the file the first argument names, "$1", whatever its name.'
SUBFOLDER_HINT = ('Read the file the first argument names, "$1": it can be a path into a '
                  "subfolder, such as logs/monday.log.")
STATUS_HINT = ("A script ends with the status of its last command: make awk the last one, and "
               "leave out the stub's exit 1.")

# Ways to choose the failed requests that a learner may write by mistake.
WRONG_CHOICES = [
    (lambda status, size: status > 400, GREATER_HINT),
    (lambda status, size: 400 <= status < 500, FIVE_XX_HINT),
    (lambda status, size: status >= 500, FOUR_XX_HINT),
    (lambda status, size: size >= 400, FIELD_HINT),
]


def mistake(run, name, requests):
    """A hint for a mistake the run shows, whatever the test is about."""
    if " " in name and name_error(run):
        return spaces_hint(name)
    got, expected = lines(run.stdout), report(requests)
    if got == expected:
        return None
    if got == expected[::-1]:
        return ORDER_HINT
    if len(got) > 2:
        return END_HINT
    if any(re.fullmatch(r"(total|errors): *bytes", line) for line in got):
        return ZERO_HINT
    if len(got) != 2:
        return None
    choices = {hint for counts, hint in WRONG_CHOICES
               if got[1] == f"errors: {errors_sum(requests, counts)} bytes" != expected[1]}
    if len(choices) == 1:  # only when the output points to one mistake
        return choices.pop()
    if got[1] == expected[1] and len(requests) > 1:
        if got[0] == f"total: {status_and_size(requests[-1])[1]} bytes":
            return PLUS_HINT
        if got[0] == f"total: {errors_sum(requests, lambda status, size: status < 400)} bytes":
            return TOTAL_HINT
    return None


def check_bytes(name, files, hint=None):
    """Run bytes.sh on `name` in a folder holding `files`, and fail unless it
    printed the two sums of the requests in `name`, nothing to stderr,
    exited with 0 and left every file as it was."""
    requests = lines(files[name])
    run = run_script(BYTES, name, files=files)
    check_run(run, report(requests), hint, mistake(run, name, requests), STATUS_HINT)


def check_requests(requests, hint):
    check_bytes("access.log", {"access.log": log(*requests)}, hint)


@pytest.mark.objective(1, 2, 3)
@pytest.mark.parametrize(
    "name, requests, hint",
    [
        ("access.log", EXAMPLE, EXAMPLE_HINT),
        ("clean.log", CLEAN, NO_ERRORS_HINT),
    ],
    ids=["access-log", "clean-log"],
)
def test_the_examples(name, requests, hint):
    check_bytes(name, {name: log(*requests), "notes.txt": NOTES}, hint)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "name, files",
    [
        ("empty day.log", {"empty day.log": ""}),
        ("empty.log", {"empty.log": "", "access.log": log(*EXAMPLE)}),
    ],
    ids=["empty-day-log", "next-to-access-log"],
)
def test_an_empty_log_prints_zeros(name, files):
    check_bytes(name, files, ZERO_HINT)


@pytest.mark.objective(1, 3)
@pytest.mark.parametrize(
    "requests",
    [
        [request(200, 512)],
        [request(404, 153, "/missing.html")],
        [request(404, 153, "/missing.html"), request(500, 2048, "/api/stats"),
         request(401, 64, "/login", method="POST")],
        [request(200, 2048, "/about.html"), request(404, 1024, "/old.html"),
         request(200, 7, "/robots.txt")],
        [request(200, 0, "/health", method="HEAD"), request(404, 0, "/missing.html"),
         request(503, 0, "/api/stats")],
        [request(status, size, f"/page/{number}.html")
         for number, (status, size) in enumerate(
             [(200, 512), (404, 153), (503, 0), (200, 1024), (401, 64), (301, 404),
              (500, 2048), (403, 7), (204, 300), (418, 99), (200, 4096), (599, 1)], start=1)],
        [request(200, 0, "/health", method="HEAD"),
         request(204, 0, "/api/items/7", method="DELETE"),
         request(201, 2048, "/files/report.txt", method="PUT"),
         request(401, 64, "/login", method="POST")],
    ],
    ids=["one-request", "one-failed-request", "every-request-failed", "last-request-smallest",
         "zero-bytes", "twelve-requests", "other-methods"],
)
def test_adds_up_the_bytes_of_every_request(requests):
    check_requests(requests, EXAMPLE_HINT)


@pytest.mark.objective(2, 3)
@pytest.mark.parametrize(
    "requests",
    [
        [request(200, 512)],
        [request(301, 2048, "/old.html"), request(200, 1024), request(304, 0, "/logo.png"),
         request(204, 0, "/api/items/7", method="DELETE")],
        [request(399, 64, "/odd.html"), request(100, 0, "/upload", method="POST")],
    ],
    ids=["one-request", "successes-and-redirects", "lowest-and-highest-below-400"],
)
def test_errors_is_0_when_no_request_failed(requests):
    check_requests(requests, NO_ERRORS_HINT)


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "status",
    [100, 200, 204, 301, 304, 399, 400, 401, 403, 404, 418, 499, 500, 502, 503, 599],
)
def test_counts_the_statuses_of_400_or_more(status):
    check_requests([ABOUT, request(status, 128, "/page.html", "192.0.2.44"), HOME], COMPARE_HINT)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "line",
    [
        request(200, 1024, "/errors/404.html"),
        request(301, 256, "/status/500"),
        request(200, 404, "/old.html"),
        request(302, 500, "/moved.html"),
        request(200, 4096, "/logo.png"),
        request(204, 1450, "/api/items/7", method="DELETE"),
        request(200, 64, "/index.html", ip="45.79.10.4"),
        request(404, 200, "/api/200"),
        request(500, 12, "/upload", method="POST"),
        request(401, 64, "/login", method="POST"),
    ],
    ids=["404-in-the-path", "500-in-the-path", "bytes-404", "bytes-500", "bytes-4096",
         "bytes-1450", "ip-starting-with-4", "failed-with-200-in-the-path-and-bytes",
         "5xx-with-few-bytes", "4xx-with-few-bytes"],
)
def test_only_the_status_field_decides(line):
    check_requests([ABOUT, line, HOME], ONLY_STATUS_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "requests",
    [
        [request(200, 600000000), request(503, 399999999, "/api/stats"),
         request(404, 1, "/missing.html")],
        [request(500, 999999999, "/api/stats"), request(200, 1)],
    ],
    ids=["total-of-one-billion", "errors-just-under-one-billion"],
)
def test_prints_large_sums_in_full(requests):
    check_requests(requests, LARGE_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "name, files, hint",
    [
        ("monday.log", {"monday.log": log(monday(200, 2048), monday(404, 153)),
                        "access.log": log(*EXAMPLE)}, ARGUMENT_HINT),
        ("logs/monday.log", {"logs/monday.log": log(monday(500, 64), monday(200, 1024)),
                             "access.log": log(*EXAMPLE)}, SUBFOLDER_HINT),
        ("monday log.log", {"monday log.log": log(monday(200, 512), monday(403, 7))},
         spaces_hint("monday log.log")),
        ("monday  log.log", {"monday  log.log": log(monday(401, 64), monday(200, 4096))},
         spaces_hint("monday  log.log")),
        ("  tuesday   log.log", {"  tuesday   log.log": log(*CLEAN)},
         spaces_hint("  tuesday   log.log")),
        ("logs/monday log.log", {"logs/monday log.log": log(*EXAMPLE)},
         spaces_hint("logs/monday log.log")),
        ("*.log", {"*.log": log(monday(200, 300), monday(410, 20)),
                   "access.log": log(*EXAMPLE)}, glob_hint("*.log", "access.log")),
        ("day?.log", {"day?.log": log(monday(503, 99), monday(200, 1)),
                      "day1.log": log(monday(404, 5000))}, glob_hint("day?.log", "day1.log")),
        ("[old].log", {"[old].log": log(monday(200, 70), monday(400, 30)),
                       "o.log": log(monday(500, 800))}, glob_hint("[old].log", "o.log")),
    ],
    ids=["not-access-log", "in-a-subfolder", "a-space", "two-spaces-in-a-row",
         "spaces-at-the-start-and-in-a-row", "a-space-in-a-subfolder", "star-as-a-name",
         "question-mark-in-a-name", "brackets-in-a-name"],
)
def test_reads_the_file_given(name, files, hint):
    check_bytes(name, files, hint)
