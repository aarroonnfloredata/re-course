"""Structural checks for exercise/receipt.py: the targets the task states."""

import pytest

from refactoring import fail, function, functions, max_length, no_comments

EXERCISE = "exercise/receipt.py"


@pytest.mark.objective(2, 3)
def test_no_function_is_longer_than_10_lines():
    max_length(EXERCISE, 10)


@pytest.mark.objective(3)
def test_no_comments_inside_functions():
    no_comments(EXERCISE)


@pytest.mark.objective(3)
def test_print_receipt_calls_extracted_functions():
    extracted = set(functions(EXERCISE)) - {"print_receipt"}
    called = function(EXERCISE, "print_receipt").calls & extracted
    if len(called) < 2:
        fail(f"print_receipt() calls {len(called)} other functions of {EXERCISE}; the "
             "task asks for its parts to move into functions of their own.\n"
             "Hint: each comment in the old print_receipt() marks a part to extract.")
