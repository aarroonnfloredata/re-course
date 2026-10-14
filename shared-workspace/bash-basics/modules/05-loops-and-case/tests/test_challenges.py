"""Checks for the inline challenges in lesson.md."""

import re

import pytest

from checks import check_files_unchanged, check_in_folder, log
from helpers import check, lines, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

# Requests from the examples in the challenge files.
INDEX = "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512"
MISSING = "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153"
FAVICON = "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153"
UPLOAD = "2026-10-06T10:17:03 198.51.100.7 POST /upload 500 0"
MONDAY_INDEX = "2026-10-05T09:12:44 192.0.2.44 GET /index.html 200 512"

# More requests.
OLD_PAGE = "2026-10-05T09:13:02 203.0.113.5 GET /old/page.html 404 153"
ROBOTS = "2026-10-06T10:19:40 198.51.100.7 GET /robots.txt 404 153"
LOGIN = "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64"
ABOUT = "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 404"  # 404 as the bytes
ERROR_PAGE = "2026-10-06T10:16:48 192.0.2.44 GET /errors/404.html 200 1024"  # 404 in the path
LOGO = "2026-10-06T10:18:30 198.51.100.7 GET /logo.png 200 4040"  # bytes start with 404
VIDEO = "2026-10-06T10:18:41 192.0.2.44 GET /video.mp4 200 5120"
BACKUP = "2026-10-06T10:19:02 203.0.113.5 GET /backup.tar 200 1048576"

NOTES = log("Look into the 404s.")

# What bash and grep print to stderr when a name with spaces is split.
NAME_ERRORS = ["No such file", "ambiguous redirect", "too many arguments",
               "binary operator expected", "unary operator expected"]


def name_error(run):
    return any(error in run.stderr for error in NAME_ERRORS)


# c1


def c1_line(name, n):
    return f"{name}: {n} requests with status 404"


C1_LOOP_HINT = ('Loop over the files with for file in *.log, and print one line for each: '
                'grep -c " 404 " "$file" counts its 404 requests.')
C1_NO_MATCH_HINT = ('When no file name ends in .log, the glob *.log stays as it is and the loop '
                    'runs once, with "*.log" itself in the variable. Skip it with '
                    "[[ -e $file ]] || continue.")
C1_SPACES_HINT = ('Loop over the glob itself, not over $(ls), and put $file in double quotes '
                  'wherever you use it: "$file" keeps a name with spaces in one piece, its runs '
                  "of spaces too.")
C1_PATTERN_HINT = ('Count the lines that contain " 404 ", with a space on each side: 404 in the '
                   "path, or as the bytes at the end of the line, doesn't count.")
C1_OTHER_FILES_HINT = ("*.log matches only the names that end in .log: notes.txt and "
                       "access.log.old are left out.")
C1_STATUS_HINT = ("Exit with status 0. A script ends with the status of its last command: "
                  "[[ -e $file ]] && ... comes out as 1 when the test fails, "
                  "[[ -e $file ]] || continue doesn't.")


def c1_problem(run):
    """A hint for a mistake the run shows whatever the case is about."""
    if "*.log" in run.stdout + run.stderr:
        return C1_NO_MATCH_HINT
    if name_error(run):
        return C1_SPACES_HINT
    return None


def check_c1(files, expected, hint):
    run = run_script(C1, files=files)
    problem = c1_problem(run)
    check_in_folder(run, stdout="".join(f"{line}\n" for line in expected), status=run.status,
                    hint=problem or hint)
    check_in_folder(run, stderr="", status=run.status, hint=problem)
    check_in_folder(run, status=0, hint=C1_STATUS_HINT)
    check_files_unchanged(run)


@pytest.mark.objective(1)
def test_c1_reports_the_404s_of_each_log_file():
    check_c1({"access.log": log(INDEX, MISSING, FAVICON), "monday log.log": log(MONDAY_INDEX),
              "notes.txt": NOTES},
             [c1_line("access.log", 2), c1_line("monday log.log", 0)], C1_LOOP_HINT)
    check_c1({"notes.txt": NOTES}, [], C1_NO_MATCH_HINT)
    check_c1({}, [], C1_NO_MATCH_HINT)
    check_c1({"access.log.old": log(MISSING, FAVICON),
              "monday  log.log": log(OLD_PAGE, INDEX, ROBOTS),
              "tuesday.log": log(FAVICON), "notes.txt": NOTES},
             [c1_line("monday  log.log", 2), c1_line("tuesday.log", 1)], C1_OTHER_FILES_HINT)
    check_c1({"  tuesday   log.log": log(MISSING, ROBOTS, FAVICON), "notes.txt": NOTES},
             [c1_line("  tuesday   log.log", 3)], C1_SPACES_HINT)
    check_c1({"access.log": log(ABOUT, ERROR_PAGE, MISSING, LOGO), "empty.log": ""},
             [c1_line("access.log", 1), c1_line("empty.log", 0)], C1_PATTERN_HINT)


# c2


C2_LINE = re.compile(r"^(.*): (\S*) requests, (\S*) bytes$")

C2_LOOP_HINT = ('Read the file with while read -r ... done < "$1": count one request for each '
                "line, and add its bytes, the sixth field, to the total.")
C2_ZERO_HINT = ("Set both counters to 0 before the loop. With an empty file the loop body never "
                "runs, and a variable that was never set prints as nothing.")
C2_PIPE_HINT = ('Put < "$1" after done instead of piping into the loop: a loop at the end of a '
                "pipe runs in a subshell, and its counts are lost when it ends.")
C2_ARITH_HINT = "Add with arithmetic, (( total += bytes )): total=$total+$bytes only joins text."
C2_FIELD_HINT = ("Bytes is the sixth field, the last one: read -r _ _ _ _ _ bytes puts it in "
                 "bytes. The status is the fifth.")
C2_SPACES_HINT = ('Put $1 in double quotes wherever you use it, < "$1" after done and in the '
                  "echo: it keeps a name with spaces in one piece, its runs of spaces too.")


def c2_problem(run, expected):
    """A hint for a mistake the run shows whatever the case is about."""
    if name_error(run):
        return C2_SPACES_HINT
    if "+" in run.stdout:
        return C2_ARITH_HINT
    printed = [C2_LINE.match(line) for line in lines(run.stdout)]
    if len(printed) == 1 and printed[0]:
        numbers = printed[0].group(2, 3)
        if "" in numbers:
            return C2_ZERO_HINT
        if numbers == ("0", "0") and not expected.endswith(": 0 requests, 0 bytes"):
            return C2_PIPE_HINT
    return None


def check_c2(name, files, expected, hint):
    run = run_script(C2, name, files=files)
    problem = c2_problem(run, expected)
    check_in_folder(run, stdout=expected, status=run.status, hint=problem or hint)
    check_in_folder(run, stderr="", status=run.status, hint=problem)
    check_in_folder(run, status=0)
    check_files_unchanged(run)


@pytest.mark.objective(3)
def test_c2_counts_the_requests_and_adds_up_their_bytes():
    check_c2("access.log", {"access.log": log(INDEX, MISSING, UPLOAD), "notes.txt": NOTES},
             "access.log: 3 requests, 665 bytes", C2_LOOP_HINT)
    check_c2("empty.log", {"empty.log": "", "access.log": log(INDEX)},
             "empty.log: 0 requests, 0 bytes", C2_ZERO_HINT)
    check_c2("  monday   log.log", {"  monday   log.log": log(MONDAY_INDEX)},
             "  monday   log.log: 1 requests, 512 bytes", C2_SPACES_HINT)
    check_c2("access.log", {"access.log": log(ABOUT, ERROR_PAGE, VIDEO, LOGIN, UPLOAD, BACKUP)},
             "access.log: 6 requests, 1055188 bytes", C2_FIELD_HINT)


# c3


C3_PAGE_HINT = ("A path is a page when it ends in .html or in /: the patterns *.html and */ "
                "match those.")
C3_IMAGE_HINT = "A path is an image when it ends in .png, .jpg or .gif: *.png|*.jpg|*.gif."
C3_END_HINT = ("A case pattern must match the whole path, so *.html matches only paths that end "
               "in .html. A path with more after .html or .png, or without the dot, is other.")
C3_CASE_HINT = ("Upper and lower case letters differ: /LOGO.PNG is other. Write the endings in "
                "lower case only.")
C3_OTHER_HINT = "Put *) last: it catches every path the other patterns missed, and prints other."


@pytest.mark.objective(4)
def test_c3_sorts_the_paths_into_kinds():
    for path, kind, hint in [
        ("/index.html", "page", C3_PAGE_HINT),
        ("/blog/", "page", C3_PAGE_HINT),
        ("/", "page", C3_PAGE_HINT),
        ("/errors/404.html", "page", C3_PAGE_HINT),
        ("/photos/cat.jpg", "image", C3_IMAGE_HINT),
        ("/logo.png", "image", C3_IMAGE_HINT),
        ("/img/spinner.gif", "image", C3_IMAGE_HINT),
        ("/api/stats", "other", C3_OTHER_HINT),
        ("/favicon.ico", "other", C3_OTHER_HINT),
        ("/index.html.bak", "other", C3_END_HINT),
        ("/logo.png?v=2", "other", C3_END_HINT),
        ("/thumbs/index.html.png", "image", C3_END_HINT),
        ("/old/cat.jpg.html", "page", C3_END_HINT),
        ("/page.xhtml", "other", C3_END_HINT),
        ("/index.htm", "other", C3_END_HINT),
        ("/photo.jpeg", "other", C3_END_HINT),
        ("/images/png", "other", C3_END_HINT),
        ("/LOGO.PNG", "other", C3_CASE_HINT),
        ("/INDEX.HTML", "other", C3_CASE_HINT),
    ]:
        run = run_script(C3, path)
        check(run, stdout=f"{path}: {kind}", stderr="", hint=hint)
        check_files_unchanged(run)
