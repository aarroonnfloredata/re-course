"""Behaviour tests for exercise/receipt.py.

They pin down what print_receipt() printed before the refactoring. They pass
on the starter file and must keep passing after every step.
"""

import pytest

from helpers import load
from refactoring import keeps_output

EXERCISE = "exercise/receipt.py"


def item(name, price, qty):
    return {"name": name, "price": price, "qty": qty}


RECEIPTS = [
    pytest.param(
        {"customer": "Ada", "items": [item("Notebook", 3.5, 2), item("Pen", 1.25, 4)],
         "code": None},
        """\
Receipt for Ada
--------------------------------
  2 x Notebook              7.00
  4 x Pen                   5.00
--------------------------------
Subtotal                   12.00
Shipping                    4.95
Total                      16.95
""",
        id="small-order-pays-shipping",
    ),
    pytest.param(
        {"customer": "Grace", "items": [item("Desk lamp", 34.0, 1), item("Bulb", 6.5, 4)],
         "code": "SAVE10"},
        """\
Receipt for Grace
--------------------------------
  1 x Desk lamp            34.00
  4 x Bulb                 26.00
--------------------------------
Subtotal                   60.00
Discount (SAVE10)          -6.00
Shipping                    0.00
Total                      54.00
""",
        id="discount-and-free-shipping",
    ),
    pytest.param(
        {"customer": "Alan", "items": [item("Mug", 12.0, 3)], "code": "SAVE10"},
        """\
Receipt for Alan
--------------------------------
  3 x Mug                  36.00
--------------------------------
Subtotal                   36.00
Shipping                    4.95
Total                      40.95
""",
        id="code-below-40-gives-no-discount",
    ),
    pytest.param(
        {"customer": "Edsger", "items": [item("Backpack", 52.0, 1)], "code": "SAVE10"},
        """\
Receipt for Edsger
--------------------------------
  1 x Backpack             52.00
--------------------------------
Subtotal                   52.00
Discount (SAVE10)          -5.20
Shipping                    4.95
Total                      51.75
""",
        id="shipping-counted-after-discount",
    ),
    pytest.param(
        {"customer": "Barbara", "items": [], "code": None},
        """\
Receipt for Barbara
--------------------------------
--------------------------------
Subtotal                    0.00
Shipping                    4.95
Total                       4.95
""",
        id="empty-order-still-pays-shipping",
    ),
    pytest.param(
        {"customer": "Linus", "items": [item("Keyboard", 45.0, 1)], "code": "save10"},
        """\
Receipt for Linus
--------------------------------
  1 x Keyboard             45.00
--------------------------------
Subtotal                   45.00
Shipping                    4.95
Total                      49.95
""",
        id="lowercase-code-gives-no-discount",
    ),
]


@pytest.mark.objective(1, 4)
@pytest.mark.parametrize("order, printed", RECEIPTS)
def test_print_receipt_prints_the_same(order, printed):
    receipt = load(EXERCISE)
    keeps_output(receipt.print_receipt, (order,), printed)
