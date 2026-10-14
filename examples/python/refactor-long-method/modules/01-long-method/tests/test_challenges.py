"""Checks for the inline challenges in lesson.md. Each checks the new
structure first, then that the behaviour stayed the same."""

import pytest

from helpers import check, load
from refactoring import fail, function, keeps, keeps_output


def require_function(module, path, name):
    if not callable(getattr(module, name, None)):
        fail(f"{path} has no {name}() yet; extract it from the commented block.")


@pytest.mark.objective(3)
def test_c1_extract_average():
    c1 = load("challenges/c1.py")
    require_function(c1, "challenges/c1.py", "average")
    check(c1.average, ([7, 9, 8],), 8.0)
    check(c1.average, ([5],), 5.0)
    if "average" not in function("challenges/c1.py", "report").calls:
        fail("report() doesn't call average(); replace the block with a call to it.")
    keeps_output(c1.report, ("Ada", [7, 9, 8]), "Ada: 3 scores, average 8.0\n")
    keeps_output(c1.report, ("Alan", [10, 3]), "Alan: 2 scores, average 6.5\n")


@pytest.mark.objective(3)
def test_c2_extract_apply_discount():
    c2 = load("challenges/c2.py")
    require_function(c2, "challenges/c2.py", "apply_discount")
    check(c2.apply_discount, (16, "HALF"), 8.0)
    check(c2.apply_discount, (3, "MINUS5"), 0,
          hint="apply_discount() returns the new total; checkout() keeps using it.")
    check(c2.apply_discount, (16, "OTHER"), 16)
    if "apply_discount" not in function("challenges/c2.py", "checkout").calls:
        fail("checkout() doesn't call apply_discount(); replace the block with a call to it.")
    keeps(c2.checkout, ([10, 6], "HALF"), 8.0)
    keeps(c2.checkout, ([10, 6], "MINUS5"), 11)
    keeps(c2.checkout, ([2, 1], "MINUS5"), 0)
    keeps(c2.checkout, ([10, 6], None), 16)
