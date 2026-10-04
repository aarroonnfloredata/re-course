"""Tests for exercise/text_tools.py."""

import pytest

from helpers import check, load

EXERCISE = "exercise/text_tools.py"


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize(
    "name, expected",
    [
        ("ada lovelace", "A.L."),
        ("Grace Brewster Hopper", "G.B.H."),
        ("plato", "P."),
        ("", ""),
    ],
)
def test_initials(name, expected):
    tools = load(EXERCISE)
    check(tools.initials, (name,), expected)


@pytest.mark.objective(4)
def test_initials_extra_whitespace():
    tools = load(EXERCISE)
    check(
        tools.initials, ("  alan   turing ",), "A.T.",
        hint="split() with no argument ignores extra whitespace.",
    )


@pytest.mark.objective(4)
@pytest.mark.parametrize(
    "title, expected",
    [
        ("Hello, World!", "hello-world"),
        ("Python 3.14: What's new?", "python-3-14-what-s-new"),
        ("already-a-slug", "already-a-slug"),
        ("!!!", ""),
    ],
)
def test_slugify(title, expected):
    tools = load(EXERCISE)
    check(tools.slugify, (title,), expected)


@pytest.mark.objective(4)
def test_slugify_extra_whitespace():
    tools = load(EXERCISE)
    check(
        tools.slugify, ("  Python   strings  ",), "python-strings",
        hint="split() with no argument ignores extra whitespace.",
    )


@pytest.mark.objective(2, 3)
@pytest.mark.parametrize(
    "text, kwargs, expected",
    [
        ("1234567890", {}, "******7890"),
        ("1234567890", {"keep": 2}, "********90"),
        ("abcdefgh", {"keep": 1}, "*******h"),
    ],
)
def test_mask(text, kwargs, expected):
    tools = load(EXERCISE)
    check(tools.mask, (text,), expected, kwargs=kwargs)


@pytest.mark.objective(2)
@pytest.mark.parametrize("text", ["1234", "12", ""])
def test_mask_short_text_unchanged(text):
    tools = load(EXERCISE)
    check(
        tools.mask, (text,), text,
        hint="If text has `keep` characters or fewer, return it unchanged.",
    )
