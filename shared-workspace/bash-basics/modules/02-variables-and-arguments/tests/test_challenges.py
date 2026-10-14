"""Checks for the inline challenges in lesson.md."""

import pytest

from helpers import check, check_file, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"

COPY = "access_2026-10-06.log"
SAVED = "saved access.log as access_2026-10-06.log"


def log(*entries):
    return "".join(f"{entry}\n" for entry in entries)


def check_prints(run, stdout, hint=None):
    """Fail unless the run printed `stdout`, nothing to stderr, and exited with
    status 0. `hint` only comes with wrong output."""
    check(run, stdout=stdout, hint=hint)
    check(run, stderr="")


@pytest.mark.objective(1)
def test_c1_saves_a_dated_copy_of_access_log():
    access = log(
        "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
        "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    )
    braces = ("In $name_$day, bash reads the name name_, an empty variable; "
              "${name}_$day marks where the name ends.")

    run = run_script(C1, files={"access.log": access})
    check_prints(run, SAVED, hint=braces)
    check_file(run, COPY, access, hint=braces)
    check_file(run, "access.log", access, hint="Copy the lines of access.log; don't move or change it.")

    earlier = log("2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048")
    run = run_script(C1, files={"access.log": access, COPY: earlier})
    check_prints(run, SAVED)
    check_file(run, COPY, access, hint="> replaces what a file held; >> adds to it.")


@pytest.mark.objective(2)
def test_c2_reports_its_arguments():
    check_prints(run_script(C2, "access.log", "404"), "404 in access.log (2 arguments)",
                 hint="STATUS is the second argument, $2, and LOGFILE the first, $1. $# counts "
                      "the arguments; the script's name isn't one of them.")
    check_prints(run_script(C2, "logs/monday.log", "500", "GET"),
                 "500 in logs/monday.log (3 arguments)",
                 hint="$# counts every argument, also the ones the line doesn't print.")
    check_prints(run_script(C2, "access.log"), " in access.log (1 arguments)",
                 hint="An argument that wasn't given expands to nothing; the spaces around it "
                      "stay.")
    check_prints(run_script(C2), " in  (0 arguments)",
                 hint="An argument that wasn't given expands to nothing; the spaces around it "
                      "stay.")


@pytest.mark.objective(3)
def test_c3_counts_get_and_post_requests():
    post = "2026-10-06T10:15:20 192.0.2.44 POST /login 401 64"
    gets = log(
        "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
        "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
        "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048",
    )
    check_prints(run_script(C3, files={"access.log": log(post) + gets}), "3 GET, 1 POST",
                 hint="Keep each count in its own variable with $( ), then print both on one "
                      "line, the GET count first.")
    check_prints(run_script(C3, files={"access.log": ""}), "0 GET, 0 POST",
                 hint="grep -c prints 0 when no line matches.")

    posts = log(
        post,
        "2026-10-06T10:16:40 203.0.113.5 POST /forms/GET 200 128",
        "2026-10-06T10:17:03 198.51.100.7 GET /favicon.ico 404 153",
    )
    check_prints(run_script(C3, files={"access.log": posts}), "1 GET, 2 POST",
                 hint='Count the lines that contain " GET ", with a space on each side, '
                      "so GET in the path doesn't count.")
