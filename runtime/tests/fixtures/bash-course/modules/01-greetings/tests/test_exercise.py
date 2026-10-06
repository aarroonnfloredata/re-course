"""Tests for exercise/greet.sh and exercise/text.sh."""

import pytest

from helpers import call, check, check_file, run_script

GREET = "exercise/greet.sh"
TEXT = "exercise/text.sh"


@pytest.mark.objective(1)
@pytest.mark.parametrize("name", ["Ada", "Grace Hopper"])
def test_greet(name):
    check(run_script(GREET, name), stdout=f"Hello, {name}!")


@pytest.mark.objective(3)
def test_greet_adds_the_guest():
    run = run_script(GREET, "Grace", files={"guests.txt": "Ada\n"})
    check(run, stdout="Hello, Grace!")
    check_file(run, "guests.txt", "Ada\nGrace\n", hint="> replaces a file; >> adds to it.")


@pytest.mark.objective(1, 3)
def test_greet_without_a_name():
    run = run_script(GREET, files={"guests.txt": "Ada\n"})
    check(run, stdout="", stderr="usage: greet.sh NAME", status=2,
          hint="$# is the number of arguments; exit sets the status.")
    check_file(run, "guests.txt", "Ada\n")


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "text, expected",
    [
        ("hello", "hello!"),
        ("good  day", "good  day!"),
    ],
)
def test_shout(text, expected):
    check(call(TEXT, "shout", text), stdout=expected)


@pytest.mark.objective(2)
@pytest.mark.parametrize(
    "stdin, expected",
    [
        ("one two\nthree\n", "2"),
        ("", "0"),
    ],
)
def test_count_lines(stdin, expected):
    check(call(TEXT, "count_lines", stdin=stdin), stdout=expected)
