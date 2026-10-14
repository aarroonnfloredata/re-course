"""Tests for exercise/scan.sh.

exercise/notfound.sh, exercise/count.sh, exercise/countall.sh,
exercise/healthcheck.sh, exercise/summary.sh, exercise/top.sh,
exercise/suspicious.sh, exercise/anonymize.sh and exercise/bytes.sh are the
finished tools of modules 1 to 9, carried over unchanged, so they have no
tests here.
"""

import posixpath
import re

import pytest

from checks import check_run, folders, inside, log, name_error, pattern_error
from helpers import lines, run_script

SCAN = "exercise/scan.sh"

NOTES = log("Look into the 503s.")
LINE = re.compile(r"(.*): (\S*) 5xx requests in (\S*) log files")


def request(status=200, size=512, path="/index.html", ip="203.0.113.5", method="GET",
            time="2026-10-06T10:15:32"):
    return f"{time} {ip} {method} {path} {status} {size}"


def status_of(line):
    return int(line.split(" ")[4])


def is_log(path, content):
    """True for a log file: a non-empty file whose name ends in .log."""
    return path.endswith(".log") and content != ""


def chosen(folder, files, choose=is_log):
    """The contents of the files under `folder` that `choose` picks."""
    return [content for path, content in files.items()
            if inside(folder, path) and choose(path, content)]


def five_xx(content, counts=lambda line: 500 <= status_of(line) <= 599):
    """The number of requests in `content` that `counts`."""
    return sum(1 for line in lines(content) if counts(line))


def report(folder, files):
    """What scan.sh prints."""
    logs = chosen(folder, files)
    return f"{folder}: {sum(map(five_xx, logs))} 5xx requests in {len(logs)} log files"


SCAN_HINT = ("find \"$1\" -type f -name '*.log' ! -empty -exec grep -c ' 5[0-9][0-9] ' {} \\; "
             "prints one count per log file. awk adds up the counts, and the number of lines "
             "it reads is the number of log files.")
FIELD_HINT = ("Count a request only when its status, the fifth field, is from 500 to 599: "
              "search for ' 5[0-9][0-9] ', with a space on each side, so that a 5xx number in "
              "the path or the bytes doesn't match.")
RANGE_HINT = "Every status from 500 to 599 is a 5xx: 5[0-9][0-9] matches all of them."
FOUR_XX_HINT = "Only statuses from 500 to 599 count: a 4xx status such as 404 doesn't."
EMPTY_HINT = "Leave out the empty .log files with ! -empty: they are not log files here."
NAME_HINT = ("Only names that end in exactly .log are log files: -name '*.log' leaves out "
             "access.log.old, server.LOG and notes.txt.")
DEPTH_HINT = ('find searches the subfolders of "$1" at any depth by itself: let its tests pick '
              'the files, instead of a glob such as "$1"/*.log.')
TYPE_HINT = "A folder is never a log file, also when its name ends in .log: add -type f."
ALL_FILES_HINT = ("F counts every log file, also the ones without a 5xx request: grep -c "
                  "prints 0 for them, and that line counts too.")
REQUESTS_HINT = ("N counts requests, not files: add up the counts that grep -c prints, "
                 "n += $1 in awk.")
PATTERN_HINT = ("Quote the pattern, -name '*.log': unquoted, bash expands *.log to the .log "
                "files in the current folder, such as today.log, before find sees it.")
WHERE_HINT = 'Search the folder from the first argument, find "$1" ..., and no other.'
DIR_HINT = 'Start the line with DIR exactly as given: echo "$1: ...", with $1 in double quotes.'
ZERO_HINT = ("When there is no log file, awk reads no lines and the sum stays empty: print it "
             "as n + 0.")
WORDS_HINT = 'The words stay the same when a number is 1: "1 5xx requests in 1 log files".'
ONE_LINE_HINT = ("Print one line: let awk add up the counts and print the result once, in an "
                 "END block.")
EACH_FILE_HINT = ("Run grep on each file on its own, with -exec ... {} \\;: with {} +, grep gets "
                  "all the files at once and puts each file's name before its count.")
NAMES_HINT = ("Let find run grep on each file, with -exec grep -c ... {} \\;: the name arrives "
              "whole, also with spaces, quotes or newlines, and nothing in it runs as code.")
SWAP_HINT = "Print N, the number of 5xx requests, first, and F, the number of log files, second."
SUM_HINT = ("Add up the counts of all the log files, n += $1 for each line awk reads, and count "
            "the lines for F.")


def quote_hint(folder):
    return (f'Put $1 in double quotes wherever you use it: "$1" keeps {folder!r} in one piece, '
            "its runs of spaces too.")


def glob_hint(folder, other):
    return (f"Put $1 in double quotes wherever you use it: quoted, the * ? [ ] in {folder!r} are "
            f"plain text. Unquoted, they make a glob that can match other folders, such as "
            f"{other}.")


def unique(hints):
    """The hint when all of `hints` agree, else None."""
    return hints.pop() if len(set(hints)) == 1 else None


# Ways to choose the log files that a learner may write by mistake.
WRONG_FILES = [
    (lambda path, content: path.endswith(".log"), EMPTY_HINT),
    (lambda path, content: ".log" in posixpath.basename(path).lower() and content != "",
     NAME_HINT),
    (lambda path, content: path.lower().endswith(".log") and content != "", NAME_HINT),
    (lambda path, content: ".log" in posixpath.basename(path) and content != "", NAME_HINT),
    (lambda path, content: content != "", NAME_HINT),
    (lambda path, content: is_log(path, content) and five_xx(content) > 0, ALL_FILES_HINT),
]

# Ways to choose the 5xx requests that a learner may write by mistake.
WRONG_REQUESTS = [
    (lambda line: re.search(r"5[0-9][0-9]", line), FIELD_HINT),
    (lambda line: re.search(r" 5[0-9][0-9]", line), FIELD_HINT),
    (lambda line: re.search(r"5[0-9][0-9] ", line), FIELD_HINT),
    (lambda line: " 5" in line, FIELD_HINT),
    (lambda line: re.search(r" 50[0-9] ", line), RANGE_HINT),
    (lambda line: " 500 " in line, RANGE_HINT),
    (lambda line: 500 < status_of(line) <= 599, RANGE_HINT),
    (lambda line: 500 <= status_of(line) < 599, RANGE_HINT),
    (lambda line: status_of(line) >= 400, FOUR_XX_HINT),
]


def scan_problem(run, folder, files):
    """A hint for a mistake the run shows, whatever the test is about."""
    if pattern_error(run):
        return PATTERN_HINT
    if name_error(run):
        return quote_hint(folder) if " " in folder else NAMES_HINT
    if "Is a directory" in run.stderr:
        return TYPE_HINT
    got = lines(run.stdout)
    if len(got) > 1:
        return EACH_FILE_HINT if any(re.search(r":\d+$", line) for line in got) else \
            ONE_LINE_HINT
    if len(got) != 1:
        return None
    match = LINE.fullmatch(got[0])
    if not match:
        return WORDS_HINT if re.search(r" request | file$", got[0]) else None
    shown_folder, got_n, got_f = match.groups()
    if shown_folder != folder:
        others = sorted(name for name in folders(files) if "/" not in name and name != folder)
        if set("*?[]") & set(folder) and others:
            return glob_hint(folder, others[0])
        return quote_hint(folder) if " " in folder else DIR_HINT
    if got_n == "":
        return ZERO_HINT
    logs = chosen(folder, files)
    n, f = sum(map(five_xx, logs)), len(logs)
    if (got_n, got_f) == (str(f), str(n)) != (str(n), str(f)):
        return SWAP_HINT
    if got_f != str(f):
        hints = [hint for choose, hint in WRONG_FILES if got_f == str(len(chosen(folder, files,
                                                                                    choose)))]
        top = [content for path, content in files.items() if inside(folder, path)
               and is_log(path, content) and "/" not in path[len(folder) + 1:]]
        if got_f == str(len(top)) and len(top) < f:
            hints.append(DEPTH_HINT)
        if folder != "." and got_f == str(len(chosen(".", files))):
            hints.append(WHERE_HINT)
        expanded = [path for path in files if "/" not in path and path.endswith(".log")]
        if len(expanded) == 1:  # what an unquoted *.log expands to
            kept = chosen(folder, files, lambda path, content: is_log(path, content)
                          and posixpath.basename(path) == expanded[0])
            if got_f == str(len(kept)):
                hints.append(PATTERN_HINT)
        return unique(hints)
    if got_n != str(n):
        hints = [hint for counts, hint in WRONG_REQUESTS
                 if got_n == str(sum(five_xx(content, counts) for content in logs))]
        if got_n == str(sum(1 for content in logs if five_xx(content))):
            hints.append(REQUESTS_HINT)
        return unique(hints)
    return None


def check_scan(folder, files, hint):
    run = run_script(SCAN, folder, files=files)
    check_run(run, [report(folder, files)], hint=hint, problem=scan_problem(run, folder, files))


# The example in scan.sh.
EXAMPLE = {
    "logs/access.log": log("2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
                           "2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0",
                           "2026-10-06T10:16:48 192.0.2.44 GET /errors/503.html 200 1024"),
    "logs/old/monday log.log": log("2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512",
                                   "2026-10-05T09:13:02 203.0.113.5 POST /upload 500 0",
                                   "2026-10-05T09:13:40 198.51.100.7 GET /api/stats 502 0"),
    "logs/old/clean.log": log("2026-10-04T18:20:31 192.0.2.44 GET /index.html 200 503"),
    "logs/empty.log": "",
    "logs/notes.txt": log("2026-10-06T10:16:20 192.0.2.44 GET /api/stats 503 0"),
    "logs/archive.log/notes.txt": NOTES,
}


@pytest.mark.objective(1, 2, 3)
@pytest.mark.parametrize(
    "folder, files",
    [
        pytest.param("logs", EXAMPLE, id="logs"),
        pytest.param("old logs", {"old logs/empty.log": ""}, id="old-logs-with-an-empty-log"),
    ],
)
def test_scan_example(folder, files):
    check_scan(folder, files, SCAN_HINT)


INDEX = request()
STATS = request(503, 0, "/api/stats", "192.0.2.44", time="2026-10-06T10:16:20")


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "files, hint",
    [
        pytest.param({"logs/access.log": log(INDEX, request(500, 0), request(501, 0),
                                             request(503, 0), request(504, 0), request(520, 0),
                                             request(550, 0), request(599, 0)),
                      "logs/old/monday.log": log(request(502, 0), INDEX)},
                     RANGE_HINT, id="every-status-from-500-to-599"),
        pytest.param({"logs/access.log": log(request(400, 153), request(401, 64),
                                             request(403, 153), request(404, 153),
                                             request(499, 0), request(301, 0), request(304, 0),
                                             request(100, 0), INDEX, STATS),
                      "logs/old/monday.log": log(request(404, 153), request(410, 153))},
                     FOUR_XX_HINT, id="other-statuses-dont-count"),
        pytest.param({"logs/access.log": log(request(200, 1024, "/errors/503.html"),
                                             request(200, 512, "/status/503"),
                                             request(404, 153, "/500"),
                                             request(301, 0, "/api/v599/items"),
                                             request(200, 64, "/5xx/550-errors.html"), STATS),
                      "logs/old/monday.log": log(request(200, 512, "/reports/2026/599"))},
                     FIELD_HINT, id="5xx-in-the-path-doesnt-count"),
        pytest.param({"logs/access.log": log(request(200, 503), request(404, 500),
                                             request(301, 599), request(200, 5120),
                                             request(200, 512), request(200, 5),
                                             request(304, 59), request(502, 503)),
                      "logs/old/monday.log": log(request(200, 550), request(201, 50000),
                                                 request(200, 512, ip="51.15.0.9"))},
                     FIELD_HINT, id="5xx-in-the-bytes-or-ip-doesnt-count"),
    ],
)
def test_scan_counts_requests_by_their_status(files, hint):
    check_scan("logs", files, hint)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "files, hint",
    [
        pytest.param({"logs/access.log": log(STATS, INDEX), "logs/access.log.old": log(STATS),
                      "logs/server.LOG": log(STATS, STATS), "logs/access.log.gz": log(STATS),
                      "logs/catalog": log(STATS), "logs/notes.txt": log(STATS, STATS, STATS),
                      "logs/old/monday.log": log(INDEX, request(502, 0)),
                      "logs/old/clean.log": log(INDEX)},
                     NAME_HINT, id="names-ending-in-exactly-.log"),
        pytest.param({"logs/access.log": log(STATS), "logs/2026/09/access.log": log(
                          request(500, 0), request(502, 0)),
                      "logs/2026/09/30/night.log": log(request(504, 0), INDEX),
                      "logs/2026/10/clean.log": log(INDEX)},
                     DEPTH_HINT, id="subfolders-at-any-depth"),
        pytest.param({"logs/access.log": log(STATS, INDEX),
                      "logs/archive.log/old.log": log(request(500, 0)),
                      "logs/archive.log/clean.log": log(INDEX),
                      "logs/archive.log/notes.txt": NOTES},
                     TYPE_HINT, id="a-folder-called-archive.log"),
        pytest.param({"today.log": log(STATS, STATS), "notes.txt": log(STATS),
                      "logs/access.log": log(STATS), "logs/old/monday.log": log(INDEX),
                      "other/access.log": log(STATS)},
                     PATTERN_HINT, id="files-outside-DIR-dont-count"),
    ],
)
def test_scan_chooses_the_log_files(files, hint):
    check_scan("logs", files, hint)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "files",
    [
        pytest.param({"logs/access.log": log(STATS, request(500, 0)), "logs/empty.log": "",
                      "logs/old/empty.log": "", "logs/old/monday.log": log(INDEX)},
                     id="some-empty"),
        pytest.param({"logs/empty.log": "", "logs/old/empty.log": "", "logs/notes.txt": ""},
                     id="only-empty"),
    ],
)
def test_scan_leaves_out_empty_log_files(files):
    check_scan("logs", files, EMPTY_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "files",
    [
        pytest.param({"logs/monday log.log": log(STATS, request(504, 0)),
                      "logs/  two  spaces.log": log(request(500, 0), INDEX),
                      "logs/old logs/  x.log": log(request(502, 0)),
                      "logs/old logs/clean  .log": log(INDEX)},
                     id="spaces"),
        pytest.param({"logs/dad's log.log": log(STATS), 'logs/say "hi".log': log(INDEX),
                      "logs/$(echo oops).log": log(request(500, 0)),
                      "logs/a;b.log": log(request(502, 0), INDEX), "logs/$HOME.log": log(INDEX),
                      "logs/it's \"$x\"; ok/access.log": log(STATS)},
                     id="quotes-dollars-and-semicolons"),
        pytest.param({"logs/-n.log": log(STATS), "logs/-v.log": log(INDEX),
                      "logs/[ab].log": log(request(500, 0)), "logs/a.log": log(INDEX),
                      "logs/*.log": log(INDEX), "logs/?.log": log(request(502, 0)),
                      "logs/-old/x:1.log": log(STATS, STATS)},
                     id="dashes-colons-and-glob-characters"),
        pytest.param({"logs/monday\nlog.log": log(STATS), "logs/old\nlogs/access.log": log(
                          request(500, 0), request(502, 0)),
                      "logs/two\nlines.log": log(INDEX), "logs/access.log": log(INDEX),
                      "logs/empty\n.log": ""},
                     id="newlines"),
    ],
)
def test_scan_handles_any_file_name(files):
    check_scan("logs", files, NAMES_HINT)


@pytest.mark.objective(1)
@pytest.mark.parametrize(
    "folder, files, hint",
    [
        pytest.param(".", {"access.log": log(STATS, request(502, 0)), "empty.log": "",
                           "notes.txt": log(STATS), "old/monday log.log": log(
                               request(500, 0), INDEX)},
                     SCAN_HINT, id="dot"),
        pytest.param("logs/october",
                     {"logs/october/access.log": log(STATS),
                      "logs/october/week 1/monday.log": log(request(500, 0), request(502, 0)),
                      "logs/september/access.log": log(request(504, 0)),
                      "logs/access.log": log(request(599, 0))},
                     DIR_HINT, id="a-path-into-a-subfolder"),
        pytest.param("  old  logs",
                     {"  old  logs/access.log": log(STATS), "  old  logs/old/x.log": log(INDEX),
                      "logs/access.log": log(request(500, 0))},
                     quote_hint("  old  logs"), id="spaces"),
        pytest.param("logs*",
                     {"logs*/access.log": log(STATS), "logs*/clean.log": log(INDEX),
                      "logs-2025/access.log": log(request(500, 0), request(502, 0))},
                     glob_hint("logs*", "logs-2025"), id="star"),
        pytest.param("logs[1]",
                     {"logs[1]/access.log": log(STATS), "logs[1]/clean.log": log(INDEX),
                      "logs1/access.log": log(request(500, 0), request(502, 0))},
                     glob_hint("logs[1]", "logs1"), id="brackets"),
    ],
)
def test_scan_searches_the_folder_given(folder, files, hint):
    check_scan(folder, files, hint)


@pytest.mark.objective(1, 2)
@pytest.mark.parametrize(
    "folder, files",
    [
        pytest.param(".", {}, id="empty-folder"),
        pytest.param("logs", {"logs/notes.txt": log(STATS), "logs/access.log.old": log(STATS),
                              "logs/empty.log": "", "logs/archive.log/notes.txt": NOTES},
                     id="no-log-files"),
    ],
)
def test_scan_without_log_files(folder, files):
    check_scan(folder, files, ZERO_HINT)


@pytest.mark.objective(3)
@pytest.mark.parametrize(
    "files, hint",
    [
        pytest.param({"logs/access.log": log(INDEX, request(404, 153)),
                      "logs/old/monday.log": log(request(301, 0))},
                     SUM_HINT, id="no-5xx"),
        pytest.param({"logs/access.log": log(STATS, INDEX), "logs/empty.log": ""},
                     WORDS_HINT, id="one-of-each"),
        pytest.param({"logs/access.log": log(STATS), "logs/clean.log": log(INDEX),
                      "logs/old/quiet.log": log(request(304, 0))},
                     ALL_FILES_HINT, id="files-without-5xx-count-too"),
        pytest.param({**{f"logs/{month:02d}/access.log": log(*[request(500 + day, 0)
                                                               for day in range(month % 4)],
                                                             INDEX)
                         for month in range(1, 13)},
                      "logs/busy.log": log(*[request(503, 0)] * 25, INDEX)},
                     SUM_HINT, id="many-files"),
    ],
)
def test_scan_adds_up_the_counts(files, hint):
    check_scan("logs", files, hint)
