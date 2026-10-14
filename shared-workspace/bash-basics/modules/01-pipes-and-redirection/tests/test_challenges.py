"""Checks for the inline challenges in lesson.md."""

import pytest

from helpers import check, check_file, run_script

C1 = "challenges/c1.sh"
C2 = "challenges/c2.sh"
C3 = "challenges/c3.sh"


def log(*entries):
    return "".join(f"{entry}\n" for entry in entries)


@pytest.mark.objective(2)
def test_c1_appends_to_archive_and_replaces_latest():
    today = log(
        "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
        "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
    )
    yesterday = log("2026-10-05T23:59:01 192.0.2.44 GET /about.html 200 2048")

    run = run_script(C1, files={"today.log": today, "archive.log": yesterday,
                                "latest.log": yesterday})
    check(run, stdout="")
    check_file(run, "archive.log", yesterday + today,
               hint=">> adds to the end of a file; > replaces what it held.")
    check_file(run, "latest.log", today,
               hint="> replaces what a file held; >> adds to it.")
    check_file(run, "today.log", today)

    run = run_script(C1, files={"today.log": today})
    check(run, stdout="")
    check_file(run, "archive.log", today, hint=">> creates the file when it doesn't exist.")
    check_file(run, "latest.log", today)


@pytest.mark.objective(3)
def test_c2_prints_post_requests_and_hides_grep_errors():
    access = log(
        "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
        "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64",
        "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048",
        "2026-10-06T10:16:40 203.0.113.5 POST /login 200 128",
    )
    posts = log(
        "2026-10-06T10:16:02 203.0.113.5 POST /login 401 64",
        "2026-10-06T10:16:40 203.0.113.5 POST /login 200 128",
    )
    check(run_script(C2, files={"access.log": access}), stdout=posts, stderr="logkit: done",
          hint='echo "logkit: done" >&2 sends the message to stderr instead of stdout.')
    check(run_script(C2), stdout="", stderr="logkit: done",
          hint="2> /dev/null throws grep's error message away.")


@pytest.mark.objective(4)
def test_c3_prints_first_two_get_requests():
    post = "2026-10-06T10:15:20 192.0.2.44 POST /login 401 64"
    gets = [
        "2026-10-06T10:15:32 203.0.113.5 GET /index.html 200 512",
        "2026-10-06T10:15:40 198.51.100.7 GET /missing.html 404 153",
        "2026-10-06T10:16:15 192.0.2.44 GET /about.html 200 2048",
    ]
    check(run_script(C3, files={"access.log": log(post, *gets)}), stdout=log(*gets[:2]),
          hint="grep picks the GET lines first; then head -n 2 keeps the first two of them.")
    check(run_script(C3, files={"access.log": log(post, gets[0])}), stdout=log(gets[0]))
    check(run_script(C3, files={"access.log": log(post)}), stdout="")
