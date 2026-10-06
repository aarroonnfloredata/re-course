"""Checks for the inline challenges in lesson.md."""

import pytest

from helpers import call, check, run_script


@pytest.mark.objective(1)
def test_c1_counts_arguments():
    check(run_script("challenges/c1.sh", "a", "b", "c"), stdout="3")
    check(run_script("challenges/c1.sh"), stdout="0")


@pytest.mark.objective(2)
def test_c2_twice():
    check(call("challenges/c2.sh", "twice", "hi"), stdout="hi hi")
    check(call("challenges/c2.sh", "twice", "42"), stdout="42 42")
