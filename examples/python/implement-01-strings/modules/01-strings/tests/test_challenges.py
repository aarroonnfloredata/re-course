"""Checks for the inline challenges in lesson.md."""

import pytest

from helpers import check, load


@pytest.mark.objective(1)
def test_c1_last_char():
    c1 = load("challenges/c1.py")
    check(c1.last_char, ("Python",), "n")
    check(c1.last_char, ("a",), "a")


@pytest.mark.objective(2)
def test_c2_middle():
    c2 = load("challenges/c2.py")
    check(c2.middle, ("Python",), "ytho")
    check(c2.middle, ("abc",), "b")
    check(
        c2.middle, ("ab",), "",
        hint="A slice never fails: when start and end meet, you get an empty string.",
    )


@pytest.mark.objective(4)
def test_c3_count_words():
    c3 = load("challenges/c3.py")
    check(c3.count_words, ("one two three",), 3)
    check(
        c3.count_words, ("  lots   of   space ",), 3,
        hint="split() with no argument treats any run of whitespace as one separator.",
    )
    check(c3.count_words, ("",), 0)
